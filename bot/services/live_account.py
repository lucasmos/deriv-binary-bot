from datetime import datetime
from bot.brokers.broker_factory import BrokerFactory
from bot.utils.error_handler import ErrorHandler
from bot.analysis.performance_tracker import PerformanceTracker

class LiveAccountService:
    def __init__(self, user):
        self.user = user
        self.broker = BrokerFactory.get_broker(user.active_broker)
        self.performance_tracker = PerformanceTracker(user.id, self.broker)
        self.error_handler = ErrorHandler('LiveAccountService')
        
    async def initialize(self):
        """Initialize connection to broker"""
        try:
            credentials = self.user.broker_accounts.get(self.user.active_broker, {})
            await self.broker.connect(credentials.get('api_key'))
            await self.performance_tracker.update_stats()
            return True
        except Exception as e:
            self.error_handler.log_error(f"Broker connection failed: {str(e)}")
            raise
        
    async def execute_trade(self, symbol, amount, direction, duration):
        """Execute real money trade"""
        try:
            if not self.broker.is_connected:
                await self.initialize()
            
            # Calculate position size based on risk management
            position_size = self._calculate_position_size(amount)
            
            # Execute trade
            result = await self.broker.place_trade(
                symbol=symbol,
                amount=position_size,
                direction=direction,
                duration=duration
            )
            
            # Update performance stats
            await self.performance_tracker.update_stats()
            
            return {
                'success': True,
                'result': result,
                'position_size': position_size
            }
        except Exception as e:
            self.error_handler.log_error(f"Trade execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_position_size(self, amount):
        """Calculate position size based on risk management"""
        balance = self.user.get_balance()
        if balance is None:
            return amount  # Can't calculate without balance
            
        risk_amount = balance * self.user.trading_preferences.get('risk_level', 0.02)
        return min(amount, risk_amount)
    
    async def get_balance(self):
        """Get current account balance"""
        try:
            if not self.broker.is_connected:
                await self.initialize()
            return await self.broker.get_balance()
        except Exception as e:
            self.error_handler.log_error(f"Balance check failed: {str(e)}")
            return None
    
    async def sync_account(self):
        """Sync account data with broker"""
        try:
            if not self.broker.is_connected:
                await self.initialize()
            
            balance = await self.broker.get_balance()
            await self.performance_tracker.update_stats()
            
            return {
                'balance': balance,
                'performance': self.performance_tracker.get_overall_performance()
            }
        except Exception as e:
            self.error_handler.log_error(f"Account sync failed: {str(e)}")
            raise