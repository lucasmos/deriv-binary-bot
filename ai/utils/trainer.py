import os
import joblib
import numpy as np
from datetime import datetime
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from ..handler import AIModelHandler

class ModelTrainer:
    def __init__(self):
        self.handler = AIModelHandler()
        self.model = None
        
    def train_from_csv(self, csv_path: str) -> bool:
        """Train model from CSV data file"""
        try:
            import pandas as pd
            df = pd.read_csv(csv_path)
            
            # Assuming last column is target and others are features
            X = df.iloc[:, :-1].values
            y = df.iloc[:, -1].values
            
            return self.train_model(X, y)
            
        except Exception as e:
            logging.error(f"CSV training error: {str(e)}")
            return False

    def train_model(self, X: np.ndarray, y: np.ndarray) -> bool:
        """Train model with numpy arrays"""
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=3,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            accuracy = self.model.score(X_test, y_test)
            logging.info(f"Model trained with accuracy: {accuracy:.2f}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_name = f"trading_model_{timestamp}.pkl"
            
            return self.handler.save_model(self.model, model_name)
            
        except Exception as e:
            logging.error(f"Training error: {str(e)}")
            return False