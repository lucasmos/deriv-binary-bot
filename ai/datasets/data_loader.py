import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ...bot.utils.logger import get_logger

logger = get_logger('ai.datasets')

def load_historical_data(symbol, timeframe, days=30):
    """Load historical market data from storage"""
    try:
        data_dir = os.path.join('ai', 'datasets', 'historical')
        file_path = os.path.join(data_dir, f"{symbol}_{timeframe}.parquet")
        
        if os.path.exists(file_path):
            df = pd.read_parquet(file_path)
            
            # Filter for recent data
            cutoff = datetime.now() - timedelta(days=days)
            df = df[df.index >= cutoff]
            
            return df
        
        return None
    except Exception as e:
        logger.error(f"Error loading historical data: {str(e)}")
        return None

def save_dataset(data, symbol, timeframe):
    """Save processed dataset to storage"""
    try:
        data_dir = os.path.join('ai', 'datasets', 'historical')
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, f"{symbol}_{timeframe}.parquet")
        
        # If file exists, append new data
        if os.path.exists(file_path):
            existing = pd.read_parquet(file_path)
            updated = pd.concat([existing, data]).drop_duplicates()
            updated.to_parquet(file_path)
        else:
            data.to_parquet(file_path)
            
        return True
    except Exception as e:
        logger.error(f"Error saving dataset: {str(e)}")
        return False