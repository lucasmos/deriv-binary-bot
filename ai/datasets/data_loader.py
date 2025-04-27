import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ...bot.utils.logger import get_logger
import pandas as pd
from pathlib import Path

logger = get_logger('ai.datasets')

def load_historical_data(data_dir: str = 'data/training') -> pd.DataFrame:
    """More robust data loading with validation"""
    data_path = Path(__file__).parent.parent / data_dir
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_path}")
        
    all_data = []
    for file in data_path.glob('*.csv'):
        try:
            df = pd.read_csv(file, parse_dates=['timestamp'])
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            all_data.append(df)
        except Exception as e:
            logging.error(f"Error loading {file}: {str(e)}")
            
    if not all_data:
        raise ValueError("No valid data files found")
        
    return pd.concat(all_data).sort_values('timestamp')
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