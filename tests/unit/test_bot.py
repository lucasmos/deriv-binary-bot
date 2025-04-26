import pytest
from bot.core.trading_engine import TradingEngine
from bot.strategies import TrendFollowingStrategy, RangeBoundStrategy
from bot.core.risk_manager import RiskManager
from unittest.mock import MagicMock

class TestBotModule:
    @pytest.fixture
    def mock_engine(self):
        engine = TradingEngine(1, MagicMock(), TrendFollowingStrategy())
        engine.broker = MagicMock()
        engine.broker.get_balance.return_value = 1000.0
        return engine

    def test_trend_following_strategy(self):
        strategy = TrendFollowingStrategy()
        signals = strategy.generate_signal(
            prices=[10, 11, 12, 13, 14],  # Upward trend
            indicators={'sma': [11, 12, 13]}
        )
        assert signals['action'] == 'buy'
        assert signals['confidence'] > 0.5

    def test_range_bound_strategy(self):
        strategy = RangeBoundStrategy()
        signals = strategy.generate_signal(
            prices=[10, 11, 10, 11, 10],  # Range-bound
            indicators={'rsi': [45, 55, 45, 55]}
        )
        assert signals['action'] in ['buy', 'sell']
        assert 0.3 < signals['confidence'] < 0.7

    def test_risk_management(self, mock_engine):
        risk_manager = RiskManager(max_risk_per_trade=0.1)  # 10% max risk
        amount = risk_manager.calculate_position_size(1000.0, 'EURUSD')
        assert amount == 100.0  # 10% of 1000

    def test_trade_execution(self, mock_engine):
        mock_engine.broker.place_trade.return_value = {'success': True, 'trade_id': 'test123'}
        result = mock_engine.execute_trade('EURUSD', 50.0)
        assert result['success'] is True
        mock_engine.broker.place_trade.assert_called_once()