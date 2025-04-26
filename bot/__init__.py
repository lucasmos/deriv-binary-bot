from flask import current_app
from .core import TradingEngine
from .brokers import BrokerFactory
from .strategies import StrategyFactory
from .analysis import PerformanceTracker

def init_bot(app):
    """Initialize the trading bot components"""
    with app.app_context():
        # Initialize broker factory
        broker_factory = BrokerFactory(app.config)
        
        # Initialize strategy factory
        strategy_factory = StrategyFactory(app.config)
        
        # Initialize trading engine
        trading_engine = TradingEngine(
            broker_factory=broker_factory,
            strategy_factory=strategy_factory,
            config=app.config
        )
        
        # Initialize performance tracker
        performance_tracker = PerformanceTracker(app.config)
        
        # Store in app context
        app.extensions['bot'] = {
            'trading_engine': trading_engine,
            'broker_factory': broker_factory,
            'strategy_factory': strategy_factory,
            'performance_tracker': performance_tracker
        }