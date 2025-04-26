import requests
import logging
from datetime import datetime
from .base_broker import BaseBroker
from ..utils import ErrorHandler

class DerivBroker(BaseBroker):
    API_URL = "https://api.deriv.com"
    DEMO_API_URL = "https://api.deriv.com"
    
    def __init__(self, config, account_type='demo'):
        super().__init__(config, account_type)
        self.api_token = config.get('DERIV_API_TOKEN')
        self.error_handler = ErrorHandler()
        
    def connect(self):
        try:
            # Test connection by fetching account info
            self.get_balance()
            self.connected = True
            return True
        except Exception as e:
            self.error_handler.log_error(e)
            self.connected = False
            return False
            
    def get_balance(self):
        endpoint = f"{self._get_base_url()}/balance"
        headers = self._get_headers()
        
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json().get('balance', {}).get('balance', 0)
        raise Exception(f"Failed to get balance: {response.text}")
        
    def get_market_data(self, symbol, timeframe='1m', count=100):
        endpoint = f"{self._get_base_url()}/ticks"
        headers = self._get_headers()
        params = {
            'symbol': symbol,
            'granularity': timeframe,
            'count': count
        }
        
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('candles', [])
        raise Exception(f"Failed to get market data: {response.text}")
        
    def place_trade(self, symbol, amount, direction, duration):
        endpoint = f"{self._get_base_url()}/trade"
        headers = self._get_headers()
        payload = {
            'symbol': symbol,
            'amount': str(amount),
            'direction': direction,
            'duration': str(duration),
            'account_type': self.account_type,
            'request_id': str(datetime.now().timestamp())
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Trade failed: {response.text}")
        
    def _get_base_url(self):
        return self.DEMO_API_URL if self.account_type == 'demo' else self.API_URL
        
    def _get_headers(self):
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }