import pandas as pd
import numpy as np
from datetime import datetime

class DataUtils:
    @staticmethod
    def normalize_data(data, method='minmax'):
        """Normalize data using specified method"""
        if method == 'minmax':
            return (data - data.min()) / (data.max() - data.min())
        elif method == 'zscore':
            return (data - data.mean()) / data.std()
        else:
            return data
            
    @staticmethod
    def resample_data(data, timeframe='1H'):
        """Resample time series data to different timeframe"""
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
            
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
            
        resampled = data.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        return resampled.reset_index().to_dict('records')
        
    @staticmethod
    def clean_market_data(data):
        """Clean and validate market data"""
        df = pd.DataFrame(data)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['timestamp'], keep='last')
        
        # Handle missing values
        df = df.ffill().bfill()
        
        # Validate data
        required_columns = ['timestamp', 'open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in market data")
            
        return df.to_dict('records')
        
    @staticmethod
    def calculate_pivot_points(data):
        """Calculate pivot points from market data"""
        df = pd.DataFrame(data)
        
        if len(df) < 2:
            return None
            
        # Calculate classic pivot points
        pp = (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
        r1 = 2 * pp - df['low'].iloc[-1]
        s1 = 2 * pp - df['high'].iloc[-1]
        r2 = pp + (df['high'].iloc[-1] - df['low'].iloc[-1])
        s2 = pp - (df['high'].iloc[-1] - df['low'].iloc[-1])
        
        return {
            'pivot': pp,
            'resistance1': r1,
            'resistance2': r2,
            'support1': s1,
            'support2': s2
        }