from abc import ABC, abstractmethod
import numpy as np
from datetime import timedelta
from deriv_api import DerivAPI

class BaseStrategy(ABC):
    def __init__(self, broker, config):
        self.broker = broker
        self.config = config
        
    @abstractmethod
    def analyze(self, data):
        pass
        
    @abstractmethod
    def execute(self):
        pass

class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, broker, config):
        super().__init__(broker, config)
        self.volatility_level = None
        self.trend_direction = None
        
    def analyze(self, data):
        # Calculate moving averages
        short_ma = data['close'].rolling(window=5).mean()
        long_ma = data['close'].rolling(window=20).mean()
        
        # Determine trend direction
        if short_ma.iloc[-1] > long_ma.iloc[-1] * 1.005:
            self.trend_direction = 'up'
        elif short_ma.iloc[-1] < long_ma.iloc[-1] * 0.995:
            self.trend_direction = 'down'
        else:
            self.trend_direction = 'neutral'
            
        # Determine volatility
        atr = (data['high'] - data['low']).rolling(window=14).mean()
        if atr.iloc[-1] > self.config['high_volatility_threshold']:
            self.volatility_level = 'high'
        elif atr.iloc[-1] > self.config['medium_volatility_threshold']:
            self.volatility_level = 'medium'
        else:
            self.volatility_level = 'low'
            
        return {
            'trend': self.trend_direction,
            'volatility': self.volatility_level
        }
        
    def execute(self):
        analysis = self.analyze(self.broker.get_recent_data())
        
        if analysis['trend'] == 'neutral':
            return None
            
        duration = self._get_duration(analysis['volatility'])
        amount = self._get_amount(analysis['volatility'])
        
        if analysis['trend'] == 'up':
            contract_type = 'CALL'
        else:
            contract_type = 'PUT'
            
        return {
            'action': 'buy',
            'contract_type': contract_type,
            'amount': amount,
            'duration': duration,
            'basis': 'stake',
            'symbol': self.config['symbol']
        }
        
    def _get_duration(self, volatility):
        # Higher volatility means shorter durations
        if volatility == 'high':
            return 1  # 1 tick
        elif volatility == 'medium':
            return 5  # 5 ticks
        else:
            return 15  # 15 ticks
            
    def _get_amount(self, volatility):
        # Higher volatility means smaller amounts
        if volatility == 'high':
            return 10  # $10
        elif volatility == 'medium':
            return 25  # $25
        else:
            return 50  # $50