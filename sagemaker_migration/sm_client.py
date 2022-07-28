import boto3
import sagemaker
import configparser
import os

base_path = os.environ['HOME']

class SageMakerMigrationClient():
    """ """
    def __init__(self, **kwargs) -> None:
        ''' '''
        profile_name = kwargs.get('profile_name', None)
        if profile_name is None:
            boto_session = boto3.session.Session()    
        else:
            boto_session = boto3.session.Session(profile_name = profile_name)
        self._region_ = boto_session.region_name
        sagemaker_session = sagemaker.Session(boto_session = boto_session)
        self._s3_client_ = boto_session.resource('s3')
        self._sm_client_ = boto3.client("sagemaker")
        
        self._default_bucket_ = sagemaker_session.default_bucket()
        config = configparser.ConfigParser()
        config.read(f'{base_path}/config.ini')
        if 'AWS' in config and 'Role' in config['AWS']:
            self._role_ = config['AWS']['Role']
        elif 'role' in kwargs:
            self._role_ = kwargs['role']
        else:
            print("No role in Config file.")
            raise Exception("Role must be provided when creating client or through config file.")

    @property
    def SageMakerS3Client(self):
        ''' '''
        return self._s3_client_.meta.client
    
    @property
    def SageMakerMigrationClient(self):
        ''' '''
        return self._sm_client_

    @property
    def Region(self):
        ''' '''
        return self._region_

    @property
    def Role(self):
        ''' '''
        return self._role_

    @property
    def DefaultBucket(self):
        ''' '''
        return self._default_bucket_

if __name__ == '__main__':
    ''' '''
    pass