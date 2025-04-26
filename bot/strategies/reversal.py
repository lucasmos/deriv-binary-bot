import numpy as np
import pandas as pd
from .base_strategy import BaseStrategy
from ..utils import TechnicalIndicators

class ReversalStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.indicators = TechnicalIndicators()
        self.reversal_period = self.config.get('reversal_period', 3)
        self.min_price_change = self.config.get('min_price_change', 0.005)  # 0.5%
        
    def analyze(self, data):
        """Identify potential trend reversals"""
        df = self.preprocess_data(data)
        
        # Calculate price changes
        df['price_change'] = df['close'].pct_change(self.reversal_period)
        
        # Check for potential reversals
        current_change = df['price_change'].iloc[-1]
        prev_change = df['price_change'].iloc[-2]
        
        if current_change > self.min_price_change and prev_change < -self.min_price_change:
            return {'direction': 'buy', 'confidence': 0.75, 'type': 'reversal'}
        elif current_change < -self.min_price_change and prev_change > self.min_price_change:
            return {'direction': 'sell', 'confidence': 0.75, 'type': 'reversal'}
            
        return None
        
    def get_parameters(self):
        return {
            'reversal_period': self.reversal_period,
            'min_price_change': self.min_price_change,
            'strategy_type': 'reversal'
        }