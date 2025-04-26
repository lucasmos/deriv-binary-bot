import numpy as np
import pandas as pd
from .base_strategy import BaseStrategy
from ..utils import TechnicalIndicators

class BreakoutStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.indicators = TechnicalIndicators()
        self.lookback_period = self.config.get('lookback_period', 20)
        self.confirmation_bars = self.config.get('confirmation_bars', 2)
        
    def analyze(self, data):
        """Identify breakout opportunities"""
        df = self.preprocess_data(data)
        
        # Calculate support/resistance levels
        df['resistance'] = df['high'].rolling(self.lookback_period).max()
        df['support'] = df['low'].rolling(self.lookback_period).min()
        
        # Check for breakouts with confirmation
        df['breakout_up'] = (df['close'] > df['resistance'].shift(1)) & \
                           (df['close'].rolling(self.confirmation_bars).min() > df['resistance'].shift(self.confirmation_bars))
        
        df['breakout_down'] = (df['close'] < df['support'].shift(1)) & \
                             (df['close'].rolling(self.confirmation_bars).max() < df['support'].shift(self.confirmation_bars))
        
        # Generate signals
        if df['breakout_up'].iloc[-1]:
            return {'direction': 'buy', 'confidence': 0.8, 'type': 'breakout'}
        elif df['breakout_down'].iloc[-1]:
            return {'direction': 'sell', 'confidence': 0.8, 'type': 'breakout'}
            
        return None
        
    def get_parameters(self):
        return {
            'lookback_period': self.lookback_period,
            'confirmation_bars': self.confirmation_bars,
            'strategy_type': 'breakout'
        }