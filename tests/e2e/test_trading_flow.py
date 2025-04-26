import pytest
from bot.core.trading_engine import TradingEngine
from bot.strategies import TrendFollowingStrategy
from ai.model import load_model
from config import TestingConfig

class TestTradingFlow:
    @pytest.fixture(autouse=True)
    def setup(self, test_app, test_db, test_user):
        self.app = test_app
        self.db = test_db
        self.user = test_user
        self.model = load_model(TestingConfig.AI_MODEL_PATH)
        self.strategy = TrendFollowingStrategy()
        self.engine = TradingEngine(self.user.id, self.model, self.strategy)

    def test_complete_trading_flow(self, mocker):
        # Mock broker API calls
        mocker.patch('bot.brokers.deriv.DerivBroker.get_balance', return_value=1000.0)
        mocker.patch('bot.brokers.deriv.DerivBroker.place_trade', return_value={'success': True, 'trade_id': 'test123'})
        mocker.patch('bot.brokers.deriv.DerivBroker.check_trade', return_value={'status': 'won', 'profit': 50.0})
        
        # Test initialization
        assert self.engine.user_id == self.user.id
        assert self.engine.balance == 1000.0
        
        # Test market analysis
        market_data = self.engine.analyze_market('EURUSD')
        assert 'signal' in market_data
        assert 'confidence' in market_data
        
        # Test trade execution
        trade_result = self.engine.execute_trade('EURUSD', 50.0)
        assert trade_result['success'] is True
        assert 'trade_id' in trade_result
        
        # Test trade monitoring
        trade_update = self.engine.monitor_trade('test123')
        assert trade_update['status'] == 'won'
        assert trade_update['profit'] == 50.0
        
        # Test balance update
        assert self.engine.balance == 1050.0