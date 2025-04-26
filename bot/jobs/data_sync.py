import time
import logging
from datetime import datetime, timedelta
from ..brokers import BrokerFactory
from ..utils import Cache

class DataSyncJob:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.broker_factory = BrokerFactory(config)
        self.cache = Cache(config)
        self.symbols = config.get('SYMBOLS', ['EURUSD', 'GBPUSD', 'USDJPY'])
        
    def run(self):
        """Run data sync job"""
        self.logger.info("Starting data sync job")
        
        broker = self.broker_factory.get_broker()
        
        while True:
            try:
                for symbol in self.symbols:
                    self._sync_symbol_data(broker, symbol)
                    
                # Sleep for 1 minute between syncs
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Data sync error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retrying
                
    def _sync_symbol_data(self, broker, symbol):
        """Sync market data for a specific symbol"""
        # Get last cached timestamp
        last_timestamp = self.cache.get(f'last_sync_{symbol}')
        
        # Get new data from broker
        new_data = broker.get_market_data(symbol, timeframe='1m', count=1440)  # 24 hours of 1m data
        
        if new_data:
            # Process and store data
            processed = self._process_data(new_data, last_timestamp)
            
            if processed:
                # Update cache
                latest_timestamp = max(item['timestamp'] for item in processed)
                self.cache.set(f'last_sync_{symbol}', latest_timestamp)
                
                # TODO: Store in database
                self.logger.info(f"Synced {len(processed)} new records for {symbol}")
                
    def _process_data(self, data, since_timestamp=None):
        """Process raw market data"""
        if since_timestamp:
            return [item for item in data if item['timestamp'] > since_timestamp]
        return data