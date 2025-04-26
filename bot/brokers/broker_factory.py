from .deriv import DerivBroker
from .quotex import QuotexBroker
from .iqoption import IQOptionBroker
from .pocketoption import PocketOptionBroker

class BrokerFactory:
    def __init__(self, config):
        self.config = config
        self.brokers = {
            'deriv': DerivBroker,
            'quotex': QuotexBroker,
            'iqoption': IQOptionBroker,
            'pocketoption': PocketOptionBroker
        }
        
    def get_broker(self, broker_name='deriv', account_type='demo'):
        """Get a broker instance by name"""
        broker_class = self.brokers.get(broker_name.lower())
        if not broker_class:
            raise ValueError(f"Unknown broker: {broker_name}")
            
        return broker_class(self.config, account_type)
        
    def get_available_brokers(self):
        """Get list of available brokers"""
        return list(self.brokers.keys())