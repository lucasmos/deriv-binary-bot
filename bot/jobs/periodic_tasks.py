import time
import logging
from datetime import datetime, timedelta
from ..brokers import BrokerFactory
from ..analysis import PerformanceTracker, MarketAnalyzer

class PeriodicTasks:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.broker_factory = BrokerFactory(config)
        self.performance_tracker = PerformanceTracker(config)
        self.market_analyzer = MarketAnalyzer(config)
        
    def run(self):
        """Run periodic maintenance tasks"""
        self.logger.info("Starting periodic tasks")
        
        while True:
            try:
                # Run tasks at different intervals
                now = datetime.utcnow()
                
                # Every hour
                if now.minute == 0:
                    self._hourly_tasks()
                
                # Every 6 hours
                if now.hour % 6 == 0 and now.minute == 0:
                    self._six_hour_tasks()
                
                # Daily at midnight UTC
                if now.hour == 0 and now.minute == 0:
                    self._daily_tasks()
                
                # Wait 1 minute between checks
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Periodic task error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying
                
    def _hourly_tasks(self):
        """Tasks to run every hour"""
        self.logger.info("Running hourly tasks")
        
        # Update performance metrics
        broker = self.broker_factory.get_broker()
        trades = broker.get_open_trades()
        for trade in trades:
            self.performance_tracker.record_trade(trade)
        
    def _six_hour_tasks(self):
        """Tasks to run every 6 hours"""
        self.logger.info("Running 6-hour tasks")
        
        # Analyze market conditions
        broker = self.broker_factory.get_broker()
        for symbol in self.config.get('SYMBOLS', ['EURUSD']):
            market_data = broker.get_market_data(symbol, timeframe='4h', count=100)
            analysis = self.market_analyzer.analyze_market_conditions(market_data)
            self.logger.info(f"Market analysis for {symbol}: {analysis}")
        
    def _daily_tasks(self):
        """Tasks to run daily"""
        self.logger.info("Running daily tasks")
        
        # Generate daily performance report
        metrics = self.performance_tracker.get_performance_metrics(period='day')
        self.logger.info(f"Daily performance metrics: {metrics}")
        
        # Reset daily tracking metrics
        self.performance_tracker.reset_daily_metrics()