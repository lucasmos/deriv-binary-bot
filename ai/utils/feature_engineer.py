import pandas as pd
import numpy as np
import talib
from ...bot.utils.logger import get_logger

logger = get_logger('ai.feature_engineer')

def add_technical_features(df):
    """Add technical indicators to DataFrame"""
    try:
        # RSI
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        
        # MACD
        macd, macd_signal, _ = talib.MACD(
            df['close'],
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            df['close'],
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        df['bb_upper'] = upper
        df['bb_lower'] = lower
        
        # Stochastic Oscillator
        slowk, slowd = talib.STOCH(
            df['high'],
            df['low'],
            df['close'],
            fastk_period=14,
            slowk_period=3,
            slowd_period=3
        )
        df['stoch_k'] = slowk
        df['stoch_d'] = slowd
        
        # ATR
        df['atr'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=14
        )
        
        # OBV
        df['obv'] = talib.OBV(df['close'], df['volume'])
        
        return df
        
    except Exception as e:
        logger.error(f"Technical feature engineering failed: {str(e)}")
        return df

def add_temporal_features(df):
    """Add time-based features to DataFrame"""
    try:
        # Time of day
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        
        # Price change features
        df['prev_close'] = df['close'].shift(1)
        df['price_change'] = df['close'] - df['prev_close']
        df['pct_change'] = df['price_change'] / df['prev_close']
        
        # Rolling features
        df['rolling_7_mean'] = df['close'].rolling(7).mean()
        df['rolling_7_std'] = df['close'].rolling(7).std()
        
        return df.dropna()
    except Exception as e:
        logger.error(f"Temporal feature engineering failed: {str(e)}")
        return df