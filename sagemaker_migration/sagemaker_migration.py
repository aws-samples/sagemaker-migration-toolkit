from cmath import e
import os
import subprocess
import sagemaker
import warnings
import time
from time import gmtime, strftime
from .sm_client import SageMakerMigrationClient
from .retrieve import *

class SageMakerMigration():

    """ """
    def __init__(self, **kwargs) -> None:
        ''' '''
        
        self.tf_versions = retrieve_tf()
        self.pt_versions = retrieve_pt()
        self.sklearn_versions = retrieve_sklearn()
        self.frameworks = ["tensorflow", "pytorch", "sklearn"]
        
        self._framework_ = kwargs['framework']
        self._version_ = kwargs['version']

        self._sm_migration_client_ = SageMakerMigrationClient(**kwargs)

        self._model_data_ = kwargs.get('model_data', None)
        self._inference_option_ = kwargs.get('inference_option', 'real-time')
        self._requirements_ = kwargs.get('requirements', None)
        self._inference_ = kwargs.get('inference', None)
        
        if self._inference_option_ == 'real-time':
            self._instance_type_ = kwargs.get('instance_type', 'ml.m5.xlarge')
            self._instance_count_ = kwargs.get('instance_count', 1)
            assert self._instance_type_ is not None, "Instance type must be provided"
            assert self._instance_count_ > 0, "Instance can't must be at least 1"

            if 'concurrency' in kwargs:
                warnings.warn("Concurrency should not be provided with real time inference. This will be ignored.")
            if 'memory_size' in kwargs:
                warnings.warn("Memory size should not be provided with real time inference. This will be ignored.")

        if self._inference_option_ == 'serverless':
            self._memory_size_ = kwargs.get('memory_size', 4096)
            self._concurrency_ = kwargs.get('concurrency', 1)
            assert not self._concurrency_ < 1, "Concurrency must be at least 1"
            assert not self._memory_size_ < 1024, "Memory size must be at least 1024mb"
            if 'instance_type' in kwargs:
                warnings.warn("Instance type should not be provided with serverless inference. This will be ignored.")
            if 'instance_count' in kwargs:
                warnings.warn("Instance count size should not be provided with serverless inference. This will be ignored.")

        if not (self._requirements_ is None):
            assert os.path.isfile(self._requirements_), "Requirements must point to a valid file"

        if not (self._inference_ is None):
            assert self._inference_.split('/')[-1] == 'inference.py', "Inference script must be named inference.py"
    
        if not (self._model_data_ is None):
            assert (os.path.isfile(self._model_data_) or os.path.isdir(self._model_data_)), "Make sure to provide a model file"

        if not (self._framework_ is None):
            assert not (self._framework_ not in self.frameworks), "The supported frameworks are: tensorflow, pytorch, sklearn"
        
        if self._framework_ == "tensorflow":
            assert not (self._version_ not in self.tf_versions), f"Please provide one of the following supported versions: {self.tf_versions}"
            
        if self._framework_ == "pytorch":
            assert not (self._version_ not in self.pt_versions), f"Please provide one of the following supported versions: {self.pt_versions}"
            
        if self._framework_ == "sklearn":
            assert not (self._version_ not in self.sklearn_versions), f"Please provide one of the following supported versions: {self.sklearn_versions}"
            
        self._sm_client_ = self._sm_migration_client_.SageMakerMigrationClient
        self._role_ = self._sm_migration_client_.Role


    def package(self):
        ''' '''
        filename = 'model.tar.gz'
        try:
            print(self._model_data_)
            print(self._inference_)
            zip_file = f"tar -cvpzf model.tar.gz {self._model_data_} {self._inference_}"
            p3 = subprocess.Popen(zip_file.split(), stdout=subprocess.PIPE)
            output, error = p3.communicate()
        except:
            print("Unable to package model folder into tarball")
        return filename

    def push_s3(self, filename):
        ''' '''
        s3_client = self._sm_migration_client_.SageMakerS3Client
        default_bucket = self._sm_migration_client_.DefaultBucket
        prefix = f'SageMakerMigration/{strftime("%Y-%m-%d-%H-%M-%S", gmtime())}'
        model_artifacts = f"s3://{default_bucket}/{prefix}/model.tar.gz"
        response = s3_client.upload_file(filename, default_bucket, f'{prefix}/model.tar.gz')
        return model_artifacts

    def create_model(self, model_artifacts):
        ''' '''
        if self._framework_ == "pytorch":
            image_uri = sagemaker.image_uris.retrieve(
            framework       = self._framework_,
            region          = self._sm_migration_client_.Region,
            version         = self._version_,
            py_version      = "py38",
            instance_type   = "ml.m5.xlarge",
            image_scope     = "inference"
            )
        else:
            image_uri = sagemaker.image_uris.retrieve(
                framework       = self._framework_,
                region          = self._sm_migration_client_.Region,
                version         = self._version_,
                py_version      = "py3",
                instance_type   = "ml.m5.xlarge",
                image_scope     = "inference"
            )
        model_name = "sm-model-" + self._framework_ + "-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        create_model_response = self._sm_client_.create_model(
            ModelName   = model_name,
            Containers  = [
                {
                    "Image"         : image_uri,
                    "Mode"          : "SingleModel",
                    "ModelDataUrl"  : model_artifacts,
                    "Environment"   : {
                        'SAGEMAKER_SUBMIT_DIRECTORY': model_artifacts,
                        'SAGEMAKER_PROGRAM': 'inference.py'
                    } 
                }
            ],
            ExecutionRoleArn = self._role_,
        )
        return model_name

    def create_endpoint_config(self, model_name):
        ''' '''
        endpoint_config = "sm-endpoint-config-" + self._framework_ + "-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        if self._inference_option_ == "real-time":
            endpoint_config_response = self._sm_client_.create_endpoint_config(
                EndpointConfigName=endpoint_config,
                ProductionVariants=[
                    {
                        "VariantName": "primaryvariant",
                        "ModelName": model_name,
                        "InstanceType": self._instance_type_,
                        "InitialInstanceCount": self._instance_count_
                    },
                ],
            )
        elif self._inference_option_ == "serverless":
            endpoint_config_response = self._sm_client_.create_endpoint_config(
                EndpointConfigName=endpoint_config,
                ProductionVariants=[
                    {
                        "VariantName": "primaryvariant",
                        "ModelName": model_name,
                        "ServerlessConfig": {
                            "MemorySizeInMB": self._memory_size_,
                            "MaxConcurrency": self._concurrency_,
                        },
                    },
                ],
            )

        else:
            raise ValueError("We only support serverless and real-time endpoints at the moment, enter one of these two options.")
            
        return endpoint_config

    def create_endpoint(self, endpoint_config_name):
        ''' '''
        endpoint_name = "sm-endpoint-" + self._framework_ + "-" + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        create_endpoint_response = self._sm_client_.create_endpoint(
            EndpointName        = endpoint_name,
            EndpointConfigName  = endpoint_config_name,
        )
        return endpoint_name, create_endpoint_response["EndpointArn"]

    # Monitoring endpoint creation
    def monitor_endpoint(self, endpoint_name):
        describe_endpoint_response = self._sm_client_.describe_endpoint(EndpointName=endpoint_name)
        while describe_endpoint_response["EndpointStatus"] == "Creating":
            describe_endpoint_response = self._sm_client_.describe_endpoint(EndpointName=endpoint_name)
            print(describe_endpoint_response["EndpointStatus"])
            time.sleep(15)
        return describe_endpoint_response

    def deploy_to_sagemaker(self):
        ''' '''
        # Package the model
        filename = self.package()
        print(filename)

        # Push model.tar.gz to S3
        print(f"Uploading {filename} to S3...")
        model_artifact = self.push_s3(filename)

        # Create model
        print("Creating model in SageMaker...")
        model_name = self.create_model(model_artifact)
        print(f"Created model: {model_name}")

        # Create endpoint config
        print("Creating endpoint config in SageMaker...")
        endpoint_config_name = self.create_endpoint_config(model_name)
        print(f"Created endpoint config: {endpoint_config_name}")

        # Create endpoint
        print("Creating endpoint in SageMaker...")
        endpoint_name, endpoint_arn = self.create_endpoint(endpoint_config_name) 
        print(f"Endpoint creation in process: {endpoint_name}")
        
        print("Monitoring endpoint creation...")
        endpoint_status = self.monitor_endpoint(endpoint_name)
        return endpoint_status
        

    @property
    def Framework(self):
        ''' '''
        return (self._framework_, self._version_)
    
if __name__ == '__main__':
    ''' '''
    pass
