from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    LSTM = "LSTM"
    GRU = "GRU"
    TRANSFORMER = "Transformer"
    LINEAR = "Linear"

@dataclass
class Hyperparameters:
    # Model architecture
    model_type: ModelType = ModelType.LSTM
    hidden_size: int = 128
    num_layers: int = 2
    dropout: float = 0.2
    
    # Training parameters
    learning_rate: float = 0.001
    batch_size: int = 64
    epochs: int = 100
    sequence_length: int = 60
    
    # Data parameters
    train_test_split: float = 0.8
    feature_columns: list = None
    target_column: str = "close"
    normalize: bool = True
    
    # Early stopping
    patience: int = 10
    min_delta: float = 0.001
    
    def to_dict(self):
        return {
            'model_type': self.model_type.value,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'sequence_length': self.sequence_length,
            'train_test_split': self.train_test_split,
            'target_column': self.target_column,
            'normalize': self.normalize,
            'patience': self.patience,
            'min_delta': self.min_delta
        }

    @classmethod
    def from_dict(cls, params):
        return cls(
            model_type=ModelType(params.get('model_type', 'LSTM')),
            hidden_size=params.get('hidden_size', 128),
            num_layers=params.get('num_layers', 2),
            dropout=params.get('dropout', 0.2),
            learning_rate=params.get('learning_rate', 0.001),
            batch_size=params.get('batch_size', 64),
            epochs=params.get('epochs', 100),
            sequence_length=params.get('sequence_length', 60),
            train_test_split=params.get('train_test_split', 0.8),
            target_column=params.get('target_column', "close"),
            normalize=params.get('normalize', True),
            patience=params.get('patience', 10),
            min_delta=params.get('min_delta', 0.001)
        )