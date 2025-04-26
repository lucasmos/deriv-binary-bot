import pytest
import numpy as np
from ai.model import TradingModel
from ai.data_processor import DataProcessor
from ai.hyperparameters import Hyperparameters

class TestAIModule:
    @pytest.fixture
    def sample_data(self):
        return np.random.rand(100, 10)  # 100 samples, 10 features

    @pytest.fixture
    def hyperparameters(self):
        return Hyperparameters()

    @pytest.fixture
    def data_processor(self):
        return DataProcessor()

    def test_data_processing(self, data_processor, sample_data):
        processed = data_processor.normalize_data(sample_data)
        assert processed.shape == sample_data.shape
        assert np.all(processed >= 0) and np.all(processed <= 1)

    def test_model_training(self, hyperparameters, sample_data):
        model = TradingModel(hyperparameters)
        X, y = sample_data[:, :-1], sample_data[:, -1]
        
        # Test training
        history = model.train(X, y, epochs=2, validation_split=0.2)
        assert 'loss' in history.history
        assert len(history.history['loss']) == 2
        
        # Test prediction
        predictions = model.predict(X[:5])
        assert predictions.shape == (5, 1)

    def test_hyperparameters(self, hyperparameters):
        params_dict = hyperparameters.to_dict()
        assert 'learning_rate' in params_dict
        assert 'batch_size' in params_dict
        
        new_params = Hyperparameters.from_dict({
            'learning_rate': 0.01,
            'batch_size': 32
        })
        assert new_params.learning_rate == 0.01
        assert new_params.batch_size == 32