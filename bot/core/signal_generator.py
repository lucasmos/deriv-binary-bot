import numpy as np
import pandas as pd
from ..utils import TechnicalIndicators

class SignalGenerator:
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators()
        
    def generate(self, market_data, strategy='trend_following'):
        """Generate trading signals based on market data"""
        if strategy == 'trend_following':
            return self._trend_following(market_data)
        elif strategy == 'mean_reversion':
            return self._mean_reversion(market_data)
        elif strategy == 'breakout':
            return self._breakout(market_data)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
            
    def _trend_following(self, data):
        """Trend following strategy implementation"""
        df = pd.DataFrame(data)
        df['sma_20'] = self.indicators.sma(df['close'], 20)
        df['sma_50'] = self.indicators.sma(df['close'], 50)
        
        df['signal'] = np.where(df['sma_20'] > df['sma_50'], 1, 0)
        df['position'] = df['signal'].diff()
        
        last_signal = df.iloc[-1]['position']
        
        if last_signal == 1:
            return {'direction': 'buy', 'confidence': 0.75}
        elif last_signal == -1:
            return {'direction': 'sell', 'confidence': 0.75}
            
        return None
        
    def _mean_reversion(self, data):
        """Mean reversion strategy implementation"""
        df = pd.DataFrame(data)
        df['sma_20'] = self.indicators.sma(df['close'], 20)
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['sma_20'] + (df['std'] * 2)
        df['lower'] = df['sma_20'] - (df['std'] * 2)
        
        last_close = df.iloc[-1]['close']
        
        if last_close > df.iloc[-1]['upper']:
            return {'direction': 'sell', 'confidence': 0.65}
        elif last_close < df.iloc[-1]['lower']:
            return {'direction': 'buy', 'confidence': 0.65}
            
        return None
        
    def _breakout(self, data):
        """Breakout strategy implementation"""
        df = pd.DataFrame(data)
        df['high_20'] = df['high'].rolling(20).max()
        df['low_20'] = df['low'].rolling(20).min()
        
        last_close = df.iloc[-1]['close']
        prev_close = df.iloc[-2]['close']
        
        if last_close > df.iloc[-1]['high_20'] and prev_close <= df.iloc[-2]['high_20']:
            return {'direction': 'buy', 'confidence': 0.8}
        elif last_close < df.iloc[-1]['low_20'] and prev_close >= df.iloc[-2]['low_20']:
            return {'direction': 'sell', 'confidence': 0.8}
            
        return None