import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
import joblib
from datetime import datetime
from ..bot.utils.logger import get_logger

logger = get_logger('ai.model')

class TradingAIModel:
    def __init__(self, input_shape=(60, 18)):
        self.model = self.build_model(input_shape)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = [
            'open', 'high', 'low', 'close', 'volume',
            'rsi', 'macd', 'macd_signal', 'adx', 'cci',
            'ema_10', 'ema_50', 'ema_200', 'bb_upper', 
            'bb_lower', 'atr', 'obv', 'vwap'
        ]
        self.log_dir = "logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
        
    def build_model(self, input_shape):
        """Build LSTM model architecture with improved layers"""
        model = Sequential([
            LSTM(256, return_sequences=True, input_shape=input_shape,
                kernel_initializer='glorot_uniform'),
            BatchNormalization(),
            Dropout(0.3),
            
            LSTM(128, return_sequences=True,
                kernel_initializer='glorot_uniform'),
            BatchNormalization(),
            Dropout(0.3),
            
            LSTM(64, return_sequences=False,
                kernel_initializer='glorot_uniform'),
            BatchNormalization(),
            Dropout(0.3),
            
            Dense(64, activation='relu'),
            Dropout(0.2),
            
            Dense(3, activation='softmax')  # 3 classes: buy, sell, hold
        ])
        
        optimizer = Adam(learning_rate=0.0005)
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'Precision', 'Recall']
        )
        
        return model
    
    def preprocess_data(self, df):
        """Prepare data for training with enhanced features"""
        # Ensure we have all required features
        missing_cols = set(self.feature_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Scale features
        scaled_data = self.scaler.fit_transform(df[self.feature_columns])
        
        # Create sequences with lookback window
        X, y = [], []
        sequence_length = input_shape[0]
        
        for i in range(sequence_length, len(scaled_data)):
            X.append(scaled_data[i-sequence_length:i])
            
            # Label based on future price movement (next 5 periods)
            future_return = (df['close'].iloc[i+5] - df['close'].iloc[i]) / df['close'].iloc[i]
            
            if future_return > 0.015:  # 1.5% increase
                y.append([1, 0, 0])  # Buy
            elif future_return < -0.015:  # 1.5% decrease
                y.append([0, 1, 0])  # Sell
            else:
                y.append([0, 0, 1])  # Hold
                
        return np.array(X), np.array(y)
    
    def train(self, X_train, y_train, X_val=None, y_val=None, 
              epochs=100, batch_size=64):
        """Train model with early stopping and checkpointing"""
        if X_val is None or y_val is None:
            from sklearn.model_selection import train_test_split
            X_train, X_val, y_train, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42
            )
            
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
            ModelCheckpoint(
                filepath='tmp/best_model.h5',
                save_best_only=True,
                monitor='val_accuracy'
            )
        ]
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Load best model
        if os.path.exists('tmp/best_model.h5'):
            self.model = load_model('tmp/best_model.h5')
            os.remove('tmp/best_model.h5')
        
        return history
    
    def predict(self, sequence):
        """Make prediction on new sequence with confidence scores"""
        if sequence.shape[1] != len(self.feature_columns):
            raise ValueError(f"Input sequence must have {len(self.feature_columns)} features")
            
        scaled_sequence = self.scaler.transform(sequence)
        prediction = self.model.predict(np.array([scaled_sequence]))
        
        return {
            'action': ['buy', 'sell', 'hold'][np.argmax(prediction)],
            'confidence': float(np.max(prediction)),
            'probabilities': {
                'buy': float(prediction[0][0]),
                'sell': float(prediction[0][1]),
                'hold': float(prediction[0][2])
            }
        }
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance with multiple metrics"""
        results = self.model.evaluate(X_test, y_test, verbose=0)
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'precision': results[2],
            'recall': results[3],
            'f1_score': 2 * (results[2] * results[3]) / (results[2] + results[3] + 1e-7)
        }
        return metrics
    
    def save(self, path='ai/models/'):
        """Save model and scaler with versioning"""
        os.makedirs(path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_path = f"{path}model_{timestamp}.h5"
        scaler_path = f"{path}scaler_{timestamp}.pkl"
        
        self.model.save(model_path)
        joblib.dump(self.scaler, scaler_path)
        
        # Save metadata
        metadata = {
            'feature_columns': self.feature_columns,
            'created_at': timestamp,
            'input_shape': self.model.input_shape[1:]
        }
        joblib.dump(metadata, f"{path}metadata_{timestamp}.pkl")
        
        return {
            'model_path': model_path,
            'scaler_path': scaler_path,
            'metadata_path': f"{path}metadata_{timestamp}.pkl"
        }
        
    def load(self, model_path, scaler_path, metadata_path):
        """Load existing model with all components"""
        from tensorflow.keras.models import load_model
        self.model = load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        
        metadata = joblib.load(metadata_path)
        self.feature_columns = metadata['feature_columns']
        
        return self