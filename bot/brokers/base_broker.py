from abc import ABC, abstractmethod
import logging

class BaseBroker(ABC):
    def __init__(self, config, account_type='demo'):
        self.config = config
        self.account_type = account_type
        self.logger = logging.getLogger(__name__)
        self.connected = False
        
    @abstractmethod
    def connect(self):
        """Connect to broker API"""
        pass
        
    @abstractmethod
    def get_balance(self):
        """Get account balance"""
        pass
        
    @abstractmethod
    def get_market_data(self, symbol, timeframe='1m', count=100):
        """Get market data for a symbol"""
        pass
        
    @abstractmethod
    def place_trade(self, symbol, amount, direction, duration):
        """Place a new trade"""
        pass
        
    @abstractmethod
    def close_trade(self, trade_id):
        """Close an open trade"""
        pass
        
    @abstractmethod
    def get_open_trades(self):
        """Get all open trades"""
        pass
        
    def switch_account(self, account_type):
        """Switch between demo and real accounts"""
        if account_type not in ['demo', 'real']:
            raise ValueError("Invalid account type")
        self.account_type = account_type
        self.logger.info(f"Switched to {account_type} account")
        return True