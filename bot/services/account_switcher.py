from bot.brokers.broker_factory import BrokerFactory
from bot.utils.error_handler import ErrorHandler

class AccountSwitcher:
    def __init__(self, user):
        self.user = user
        self.error_handler = ErrorHandler('AccountSwitcher')
        
    async def switch_account_type(self, account_type):
        """Switch between demo and real account types"""
        if account_type not in ['demo', 'real']:
            raise ValueError("Invalid account type")
            
        self.user.account_type = account_type
        return True
    
    async def switch_active_broker(self, broker_name):
        """Change the active broker for real accounts"""
        if broker_name not in self.user.broker_accounts:
            raise ValueError(f"Broker {broker_name} not linked")
            
        self.user.active_broker = broker_name
        
        # Verify broker connection
        try:
            broker = BrokerFactory.get_broker(broker_name)
            credentials = self.user.broker_accounts[broker_name]
            await broker.connect(credentials.get('api_key'))
            return True
        except Exception as e:
            self.error_handler.log_error(f"Broker switch failed: {str(e)}")
            raise