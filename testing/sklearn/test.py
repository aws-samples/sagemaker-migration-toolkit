from sagemaker_migration import frameworks as fwk
import os

if __name__ == "__main__":
    ''' '''

    # Real Time
    sk_model = fwk.SKLearnModel(
        version = "0.23-1", 
        model_data = 'model.joblib',
        inference_option = 'real-time',
        inference = 'inference.py',
        instance_type = 'ml.m5.xlarge'
    )

    # Serverless
    sk_model = fwk.SKLearnModel(
        version = "0.23-1", 
        model_data = 'model.joblib',
        inference_option = 'serverless',
        inference = 'inference.py',
        concurrency = 5
    )
    
    sk_model.deploy_to_sagemaker()