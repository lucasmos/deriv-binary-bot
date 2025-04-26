from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, config=None):
        self.config = config or {}
        
    @abstractmethod
    def analyze(self, data):
        """Analyze market data and generate signals"""
        pass
        
    @abstractmethod
    def get_parameters(self):
        """Get strategy parameters"""
        pass
        
    def preprocess_data(self, data):
        """Preprocess market data before analysis"""
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()
            
        # Convert timestamp to datetime if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
        return df