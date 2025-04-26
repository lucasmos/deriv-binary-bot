import numpy as np
import pandas as pd
from .base_strategy import BaseStrategy
from ..utils import TechnicalIndicators

class RangeBoundStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.indicators = TechnicalIndicators()
        self.range_period = self.config.get('range_period', 14)
        self.overbought_level = self.config.get('overbought_level', 70)
        self.oversold_level = self.config.get('oversold_level', 30)
        
    def analyze(self, data):
        """Identify range-bound market conditions"""
        df = self.preprocess_data(data)
        
        # Calculate RSI
        df['rsi'] = self.indicators.rsi(df['close'], self.range_period)
        
        # Identify range extremes
        current_rsi = df['rsi'].iloc[-1]
        
        if current_rsi >= self.overbought_level:
            return {'direction': 'sell', 'confidence': 0.7, 'type': 'range'}
        elif current_rsi <= self.oversold_level:
            return {'direction': 'buy', 'confidence': 0.7, 'type': 'range'}
            
        return None
        
    def get_parameters(self):
        return {
            'range_period': self.range_period,
            'overbought_level': self.overbought_level,
            'oversold_level': self.oversold_level,
            'strategy_type': 'range_bound'
        }