import numpy as np
import pandas as pd
from .base_strategy import BaseStrategy
from ..utils import TechnicalIndicators

class ScalpingStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.indicators = TechnicalIndicators()
        self.fast_ema = self.config.get('fast_ema', 5)
        self.slow_ema = self.config.get('slow_ema', 10)
        self.profit_target = self.config.get('profit_target', 0.002)  # 0.2%
        self.stop_loss = self.config.get('stop_loss', 0.001)  # 0.1%
        
    def analyze(self, data):
        """Generate scalping signals"""
        df = self.preprocess_data(data)
        
        # Calculate EMAs
        df['fast_ema'] = self.indicators.ema(df['close'], self.fast_ema)
        df['slow_ema'] = self.indicators.ema(df['close'], self.slow_ema)
        
        # Generate signals
        if df['fast_ema'].iloc[-1] > df['slow_ema'].iloc[-1] and \
           df['fast_ema'].iloc[-2] <= df['slow_ema'].iloc[-2]:
            return {
                'direction': 'buy',
                'confidence': 0.8,
                'type': 'scalping',
                'take_profit': df['close'].iloc[-1] * (1 + self.profit_target),
                'stop_loss': df['close'].iloc[-1] * (1 - self.stop_loss)
            }
        elif df['fast_ema'].iloc[-1] < df['slow_ema'].iloc[-1] and \
             df['fast_ema'].iloc[-2] >= df['slow_ema'].iloc[-2]:
            return {
                'direction': 'sell',
                'confidence': 0.8,
                'type': 'scalping',
                'take_profit': df['close'].iloc[-1] * (1 - self.profit_target),
                'stop_loss': df['close'].iloc[-1] * (1 + self.stop_loss)
            }
            
        return None
        
    def get_parameters(self):
        return {
            'fast_ema': self.fast_ema,
            'slow_ema': self.slow_ema,
            'profit_target': self.profit_target,
            'stop_loss': self.stop_loss,
            'strategy_type': 'scalping'
        }