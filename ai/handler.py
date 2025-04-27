import os
import logging
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
from typing import Optional, Any
from typing import Dict, Union
import json

class AIModelHandler:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.model_path = self.base_path / os.getenv('AI_MODEL_PATH', 'ai/models/production')
        self.training_interval = int(os.getenv('AI_TRAINING_INTERVAL', 24))
        self.current_model = None
        self.last_trained = None
        self._ensure_directories_exist()
        
    def _ensure_directories_exist(self):
        """Ensure all required directories exist"""
        self.model_path.mkdir(parents=True, exist_ok=True)
        
    def load_latest_model(self) -> Optional[Any]:
        """Load the most recent model from production directory"""
        try:
            model_files = list(self.model_path.glob('*.pkl'))
            if not model_files:
                return None
                
            latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
            with open(latest_model, 'rb') as f:
                self.current_model = pickle.load(f)
                
            self.last_trained = datetime.fromtimestamp(latest_model.stat().st_mtime)
            return self.current_model
            
        except Exception as e:
            logging.error(f"Model loading error: {str(e)}")
            return None

    def save_model(self, model: Any, model_name: str = None) -> bool:
        """Save a trained model to production directory"""
        try:
            model_name = model_name or f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            save_path = self.model_path / model_name
            
            with open(save_path, 'wb') as f:
                pickle.dump(model, f)
                
            return True
            
        except Exception as e:
            logging.error(f"Model saving error: {str(e)}")
            return False

    # Modify predict_market_trend method
def predict_market_trend(self, market_data: Dict[str, Union[float, str]]) -> Optional[float]:
    """Improved prediction with better type handling"""
    try:
        if not isinstance(market_data, dict):
            raise ValueError("Market data must be a dictionary")
            
        # Convert all values to float safely
        features = {k: float(v) for k, v in market_data.items() 
                  if k in ['open', 'high', 'low', 'close', 'volume']}
                  
        if len(features) != 5:
            logging.warning(f"Incomplete features: {json.dumps(features)}")
            return None
            
        return self._predict_from_features(list(features.values()))
        
    except (ValueError, TypeError) as e:
        logging.error(f"Data conversion error: {str(e)}")
        return None
    
def _prepare_features(self, market_data: dict) -> np.ndarray:
        """Convert market data dictionary to feature array"""
        # Implement your specific feature engineering here
        features = [
            market_data.get('open', 0),
            market_data.get('high', 0),
            market_data.get('low', 0),
            market_data.get('close', 0),
            market_data.get('volume', 0)
        ]
        return np.array(features).reshape(1, -1)