import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ..bot.brokers.broker_factory import BrokerFactory
from ..bot.utils.logger import get_logger
from .model import TradingAIModel
from ..bot.analysis.market_analyzer import MarketConditionAnalyzer
from ..bot.analysis.performance_tracker import PerformanceTracker

logger = get_logger('ai.trainer')

class AITrainer:
    def __init__(self, user=None, deriv_api_key=None):
        self.user = user
        self.api_key = deriv_api_key or os.getenv('DERIV_API_KEY')
        self.api = None
        self.model = TradingAIModel()
        self.market_analyzer = MarketConditionAnalyzer()
        self.performance_tracker = PerformanceTracker(user.id if user else None)
        
    async def initialize(self):
        """Initialize connection to Deriv API"""
        if not self.api:
            self.api = BrokerFactory.get_broker('deriv')()
            await self.api.connect(self.api_key)
        
    async def fetch_historical_data(self, symbol, timeframe='1m', days=30):
        """Fetch historical data with enhanced market features"""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            candles = await self.api.get_candles({
                'symbol': symbol,
                'timeframe': timeframe,
                'start': start_time.timestamp(),
                'end': end_time.timestamp(),
                'count': 5000
            })
            
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Add technical indicators
            df = self.market_analyzer.add_technical_indicators(df)
            
            # Add market sentiment features
            df = self.market_analyzer.add_sentiment_features(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {str(e)}")
            return None
    
    async def stream_live_data(self, symbol, callback, duration=3600):
        """Stream live data for continuous learning"""
        start_time = time.time()
        
        async def on_tick(tick):
            # Process tick data and update model
            processed = self.process_tick_data(tick)
            if processed:
                prediction = self.model.predict(processed['sequence'])
                await callback({
                    'symbol': symbol,
                    'prediction': prediction,
                    'timestamp': datetime.utcnow(),
                    'raw_data': tick
                })
                
        await self.api.subscribe_to_ticks(symbol, on_tick)
        
        # Run for specified duration
        while time.time() - start_time < duration:
            await asyncio.sleep(1)
            
        await self.api.unsubscribe(symbol)
    
    def process_tick_data(self, tick):
        """Process real-time tick data into model input format"""
        # Implementation would convert tick to proper sequence
        pass
    
    async def train_on_user_trades(self, lookback_days=30):
        """Train model on user's historical trades"""
        if not self.user:
            raise ValueError("User required for this operation")
            
        # Get user's trade history
        trades = await self.performance_tracker.get_trade_history(
            days=lookback_days
        )
        
        # Get corresponding market data
        market_data = {}
        symbols = set(trade['symbol'] for trade in trades)
        
        for symbol in symbols:
            data = await self.fetch_historical_data(symbol, days=lookback_days)
            if data is not None:
                market_data[symbol] = data
                
        # Prepare labeled dataset
        X, y = [], []
        for trade in trades:
            if trade['symbol'] not in market_data:
                continue
                
            # Get market data at trade time
            trade_time = pd.to_datetime(trade['timestamp'])
            df = market_data[trade['symbol']]
            
            # Get sequence leading up to trade
            mask = (df.index <= trade_time)
            sequence = df[mask].tail(self.model.model.input_shape[1])
            
            if len(sequence) == self.model.model.input_shape[1]:
                X.append(sequence[self.model.feature_columns].values)
                y.append([
                    1 if trade['profit'] > 0 else 0,  # win/loss
                    trade['profit'] / trade['amount']  # normalized profit
                ])
                
        if len(X) > 0:
            X = np.array(X)
            y = np.array(y)
            
            # Train model
            history = self.model.train(X, y)
            return history
            
        return None
    
    async def walk_forward_train(self, symbols, initial_days=90, 
                               retrain_interval=7, total_period=365):
        """Walk-forward training with periodic validation"""
        await self.initialize()
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=total_period)
        current_date = start_date + timedelta(days=initial_days)
        
        performance_log = []
        
        while current_date < end_date:
            # 1. Training phase
            train_start = current_date - timedelta(days=initial_days)
            logger.info(f"Training on data from {train_start} to {current_date}")
            
            train_data = []
            for symbol in symbols:
                df = await self.fetch_historical_data(
                    symbol,
                    start=train_start,
                    end=current_date
                )
                if df is not None:
                    train_data.append(df)
            
            if train_data:
                combined_data = pd.concat(train_data)
                X_train, y_train = self.model.preprocess_data(combined_data)
                
                # 2. Validation phase
                validate_end = min(current_date + timedelta(days=retrain_interval), end_date)
                val_data = []
                
                for symbol in symbols:
                    df = await self.fetch_historical_data(
                        symbol,
                        start=current_date,
                        end=validate_end
                    )
                    if df is not None:
                        val_data.append(df)
                
                if val_data:
                    val_combined = pd.concat(val_data)
                    X_val, y_val = self.model.preprocess_data(val_combined)
                    
                    # Train model
                    history = self.model.train(X_train, y_train, X_val, y_val)
                    
                    # Evaluate
                    val_metrics = self.model.evaluate(X_val, y_val)
                    
                    # Log performance
                    performance_log.append({
                        'train_start': train_start,
                        'train_end': current_date,
                        'val_start': current_date,
                        'val_end': validate_end,
                        'val_accuracy': val_metrics['accuracy'],
                        'val_f1_score': val_metrics['f1_score'],
                        'samples': len(X_train) + len(X_val)
                    })
                    
                    logger.info(f"Validation Accuracy: {val_metrics['accuracy']:.2%}, F1: {val_metrics['f1_score']:.2f}")
            
            current_date += timedelta(days=retrain_interval)
        
        # Save final model
        if self.user:
            save_path = f"ai/models/user_{self.user.id}/"
        else:
            save_path = "ai/models/"
            
        self.model.save(save_path)
        
        return performance_log
    
    async def train_with_recent_data(self, hours=24):
        """Train on most recent market data"""
        await self.initialize()
        
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'R_100']
        recent_data = []
        
        for symbol in symbols:
            df = await self.fetch_historical_data(
                symbol,
                timeframe='5m',
                start=datetime.utcnow() - timedelta(hours=hours)
            )
            if df is not None:
                recent_data.append(df)
                
        if recent_data:
            combined = pd.concat(recent_data)
            X, y = self.model.preprocess_data(combined)
            
            # Use 20% of data for validation
            val_size = int(len(X) * 0.2)
            X_train, y_train = X[:-val_size], y[:-val_size]
            X_val, y_val = X[-val_size:], y[-val_size:]
            
            history = self.model.train(X_train, y_train, X_val, y_val)
            return history
            
        return None