import pytest
from auth.services import AuthService
from payments.services import PaymentService
from bot.services import TradingService

class TestUserFlow:
    def test_complete_user_flow(self, client, test_db, test_user):
        # 1. User Registration
        auth_service = AuthService()
        registration = auth_service.register_user(
            'newuser', 'new@example.com', 'securepassword123'
        )
        assert registration['success'] is True
        
        # 2. Email Verification (mock)
        user = auth_service.get_user_by_email('new@example.com')
        auth_service.verify_email(user.id, 'mocked_token')
        assert user.is_active is True
        
        # 3. Deposit Funds
        payment_service = PaymentService()
        deposit = payment_service.process_deposit(
            user.id, 100.0, 'USD', 'stripe', 'pm_test123'
        )
        assert deposit['success'] is True
        
        # 4. Start Trading
        trading_service = TradingService(user.id)
        trading_service.set_strategy('trend_following')
        trading_service.set_amount(50.0)
        
        # Mock trading methods
        trading_service.engine.broker = MockBroker()
        result = trading_service.execute_trade('EURUSD')
        assert result['success'] is True
        
        # 5. Withdraw Profits
        withdrawal = payment_service.process_withdrawal(
            user.id, 30.0, 'USD', 'stripe', {'account': 'acct_test123'}
        )
        assert withdrawal['success'] is True

class MockBroker:
    def get_balance(self):
        return 100.0
    
    def place_trade(self, symbol, amount):
        return {'success': True, 'trade_id': 'mock123'}
    
    def check_trade(self, trade_id):
        return {'status': 'won', 'profit': 10.0}