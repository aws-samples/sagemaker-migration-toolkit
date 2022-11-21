import sagemaker


def retrieve_tf():
    tf_versions = []
    tf_images = sagemaker.image_uris.config_for_framework(framework="tensorflow")['inference']['versions']
    for version,metadata in tf_images.items():
        tf_versions.append(version)
    return tf_versions
    

def retrieve_pt():
    pytorch_versions = []
    pytorch_images = sagemaker.image_uris.config_for_framework(framework="pytorch")['inference']['versions']
    for version,metadata in pytorch_images.items():
        pytorch_versions.append(version)
    return pytorch_versions
    
def retrieve_sklearn():
    sklearn_versions = []
    sklearn_images = sagemaker.image_uris.config_for_framework(framework="sklearn")['inference']['versions']
    for version,metadata in sklearn_images.items():
        sklearn_versions.append(version)
    return sklearn_versions

#print(retrieve_tf())
#print(retrieve_pt())
#print(retrieve_sklearn())
        
