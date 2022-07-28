from sagemaker_migration import frameworks as fwk
import os

if __name__ == "__main__":
    ''' '''

    # Real Time

    tf_model = fwk.TensorFlowModel(
        version = "2.8.0", 
        model_data = '0000001',
        inference_option = 'real-time',
        inference = 'inference.py',
        instance_type = 'ml.m5.xlarge'
    )


    # Serverless
    tf_model = fwk.TensorFlowModel(
        version = "2.8.0", 
        model_data = '0000001',
        inference_option = 'serverless',
        inference = 'inference.py',
        concurrency = 5
    )
    
    tf_model.deploy_to_sagemaker()