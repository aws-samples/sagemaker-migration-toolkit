import os
from .sagemaker_migration import SageMakerMigration


class SKLearnModel(SageMakerMigration):
    """ """
    def __init__(self, **kwargs) -> None:
        kwargs['framework'] = 'sklearn'
        assert 'version' in kwargs, "Framework version must be specified."
        assert 'model_data' in kwargs, "Folder with model data must be provided"
        
        ## Retrieve list of versions from SM
        ## Check if version in list of versions

        super().__init__(**kwargs)

    def _check_artifact_(self):
        ''' '''
        print("Model data contains: ", self._model_data_)
        if "joblib" not in self._model_data_:
            raise ValueError("Your sklearn model artifact needs to be in joblib format")
        return True

    def package(self):
        self._check_artifact_()
        return super().package()


class TensorFlowModel(SageMakerMigration):
    """ """
    def __init__(self, **kwargs) -> None:
        kwargs['framework'] = 'tensorflow'
        assert 'version' in kwargs, "Framework version must be specified."
        assert 'model_data' in kwargs, "Folder with model data must be provided"
        
        ## Retrieve list of versions from SM
        ## Check if version in list of versions

        super().__init__(**kwargs)

    def _check_artifact_(self):
        ''' '''
        print("Model data contains: ", self._model_data_)
        tf_files = ['variables', 'keras_metadata.pb', 'saved_model.pb']
        if os.path.isdir(self._model_data_):
            files = os.listdir(self._model_data_)
            print(files)
            if all(elem in files for elem in tf_files):
                return True
            return False
        return False

    def package(self):
        self._check_artifact_()
        return super().package()


class PyTorchModel(SageMakerMigration):
    """ """
    def __init__(self, **kwargs) -> None:
        kwargs['framework'] = 'pytorch'
        assert 'version' in kwargs, "Framework version must be specified."
        assert 'model_data' in kwargs, "Folder with model data must be provided"
        
        ## Retrieve list of versions from SM
        ## Check if version in list of versions

        super().__init__(**kwargs)

    def _check_artifact_(self):
        ''' '''
        print("Model data contains: ", self._model_data_)
        if "pth" not in self._model_data_:
            raise ValueError("Your pytorch model artifact needs to be in .pth format")
        return True

    def package(self):
        self._check_artifact_()
        return super().package()


if __name__ == "__main__":
    ''' '''