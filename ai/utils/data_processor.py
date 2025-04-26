import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from ...bot.utils.logger import get_logger

logger = get_logger('ai.data_processor')

def preprocess_data(df, features=None, target='close', lookback=60):
    """Preprocess raw market data for training"""
    try:
        if features is None:
            features = [
                'open', 'high', 'low', 'close', 'volume',
                'rsi', 'macd', 'adx', 'ema_10', 'ema_50'
            ]
        
        # Handle missing values
        df = df[features + [target]].dropna()
        
        # Normalize features
        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(df[features])
        
        # Create sequences
        X, y = [], []
        for i in range(lookback, len(df)):
            X.append(scaled_features[i-lookback:i])
            y.append(df[target].iloc[i] > df[target].iloc[i-1])  # Binary classification
            
        return np.array(X), np.array(y), scaler
        
    except Exception as e:
        logger.error(f"Data preprocessing failed: {str(e)}")
        raise

def normalize_data(data, scaler=None):
    """Normalize data using scaler"""
    if scaler is None:
        scaler = StandardScaler()
        return scaler.fit_transform(data), scaler
    return scaler.transform(data), scaler

def create_sequences(data, seq_length):
    """Create time series sequences from data"""
    sequences = []
    for i in range(len(data) - seq_length):
        sequences.append(data[i:i+seq_length])
    return np.array(sequences)