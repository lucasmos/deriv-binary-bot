import requests
import logging
from datetime import datetime
from .base_broker import BaseBroker
from ..utils import ErrorHandler

class IQOptionBroker(BaseBroker):
    API_URL = "https://api.iqoption.com/api"
    
    def __init__(self, config, account_type='demo'):
        super().__init__(config, account_type)
        self.email = config.get('IQOPTION_EMAIL')
        self.password = config.get('IQOPTION_PASSWORD')
        self.error_handler = ErrorHandler()
        self.session = requests.Session()
        
    def connect(self):
        try:
            # Authenticate
            auth_url = f"{self.API_URL}/v1.0/login"
            payload = {
                'email': self.email,
                'password': self.password
            }
            response = self.session.post(auth_url, data=payload)
            
            if response.status_code != 200:
                raise Exception("Authentication failed")
                
            self.connected = True
            return True
        except Exception as e:
            self.error_handler.log_error(e)
            self.connected = False
            return False
            
    def get_balance(self):
        if not self.connected:
            self.connect()
            
        url = f"{self.API_URL}/v1.0/profile"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json().get('balance', 0)
        raise Exception(f"Failed to get balance: {response.text}")
        
    def get_market_data(self, symbol, timeframe='1m', count=100):
        url = f"{self.API_URL}/v1.0/candles"
        params = {
            'symbol': symbol,
            'timeframe': timeframe,
            'count': count
        }
        response = self.session.get(url, params=params)
        
        if response.status_code == 200:
            return response.json().get('candles', [])
        raise Exception(f"Failed to get market data: {response.text}")
        
    def place_trade(self, symbol, amount, direction, duration):
        url = f"{self.API_URL}/v1.0/order"
        payload = {
            'symbol': symbol,
            'amount': amount,
            'direction': direction,
            'duration': duration,
            'type': 'digital' if self.account_type == 'demo' else 'binary'
        }
        response = self.session.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Trade failed: {response.text}")