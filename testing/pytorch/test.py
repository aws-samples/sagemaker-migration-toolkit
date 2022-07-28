from sagemaker_migration import frameworks as fwk
import os

if __name__ == "__main__":
    ''' '''

    # Real-Time
    pt_model = fwk.PyTorchModel(
        version = "1.11.0", 
        model_data = 'model.pth',
        inference_option = 'real-time',
        inference = 'inference.py',
        instance_type = 'ml.m5.xlarge'
    )


    # Serverless
    
    pt_model = fwk.PyTorchModel(
        version = "1.11.0", 
        model_data = 'model.pth',
        inference_option = 'serverless',
        inference = 'inference.py',
        concurrency = 5
    )
    
    pt_model.deploy_to_sagemaker()