import asyncio
import time
from datetime import datetime, timedelta
import pandas as pd
from ..bot.utils.logger import get_logger
from .models import TradingAIModel
from .trainer import AITrainer
from .validator import WalkForwardValidator
from ..bot.analysis.market_analyzer import MarketConditionAnalyzer

logger = get_logger('ai.pipeline')

class ContinuousLearning:
    def __init__(self, evaluation_threshold=0.65, retrain_interval=24):
        self.threshold = evaluation_threshold
        self.retrain_interval = retrain_interval  # hours
        self.last_retrain = None
        self.trainer = None
        self.validator = WalkForwardValidator()
        self.market_analyzer = MarketConditionAnalyzer()
        
    async def initialize(self):
        """Initialize trainer with current user/model"""
        from app import current_app
        self.trainer = current_app.ai_trainer
        
    async def daily_improvement_cycle(self):
        """Continuous learning loop"""
        await self.initialize()
        
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Check if we need to retrain
                if self.last_retrain is None or \
                   (current_time - self.last_retrain) > timedelta(hours=self.retrain_interval):
                    
                    logger.info("Starting model improvement cycle")
                    
                    # 1. Collect new data
                    new_data = await self.collect_training_data()
                    
                    if new_data is not None and len(new_data) > 0:
                        # 2. Evaluate current model
                        current_perf = await self.evaluate_current_model(new_data)
                        logger.info(f"Current model performance: {current_perf}")
                        
                        if current_perf['mean_accuracy'] < self.threshold:
                            # 3. Retrain model
                            await self.trainer.train_with_recent_data()
                            
                            # 4. Validate new model
                            new_perf = await self.evaluate_current_model(new_data)
                            logger.info(f"New model performance: {new_perf}")
                            
                            # 5. Deploy if improved
                            if new_perf['mean_accuracy'] > current_perf['mean_accuracy']:
                                await self.deploy_new_model()
                                self.last_retrain = datetime.utcnow()
                
                # Sleep until next check
                await asyncio.sleep(3600)  # Check hourly
                
            except Exception as e:
                logger.error(f"Error in improvement cycle: {str(e)}")
                await asyncio.sleep(600)  # Retry after 10 minutes on error
    
    async def collect_training_data(self, lookback_hours=48):
        """Collect recent trading data for training"""
        try:
            # 1. Get successful trades from database
            from ..payments.models import Transaction
            successful_trades = Transaction.query.filter(
                Transaction.status == 'completed',
                Transaction.created_at >= datetime.utcnow() - timedelta(hours=lookback_hours)
            ).all()
            
            # 2. Get corresponding market data
            market_data = []
            for trade in successful_trades:
                data = await self.market_analyzer.get_market_data(
                    symbol=trade.metadata.get('symbol'),
                    start=trade.created_at - timedelta(minutes=60),
                    end=trade.created_at
                )
                if data is not None:
                    market_data.append({
                        'trade': trade,
                        'market_data': data
                    })
            
            # 3. Format for training
            formatted_data = self._format_training_data(market_data)
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error collecting training data: {str(e)}")
            return None
    
    def _format_training_data(self, raw_data):
        """Format raw trade/market data for training"""
        X, y = [], []
        
        for item in raw_data:
            trade = item['trade']
            market_data = item['market_data']
            
            # Get sequence of market data leading to trade
            sequence = market_data[self.trainer.model.feature_columns].values
            
            # Create label based on trade outcome
            if trade.metadata.get('result') == 'win':
                if trade.metadata.get('direction') == 'CALL':
                    y.append([1, 0, 0])  # Buy
                else:
                    y.append([0, 1, 0])  # Sell
            else:
                y.append([0, 0, 1])  # Hold
                
            X.append(sequence)
            
        return np.array(X), np.array(y)
    
    async def evaluate_current_model(self, validation_data):
        """Evaluate model on new data"""
        if validation_data is None or len(validation_data[0]) == 0:
            return {'mean_accuracy': 0, 'mean_f1': 0}
            
        X, y = validation_data
        return self.validator.validate(self.trainer.model, X, y)
    
    async def deploy_new_model(self):
        """Deploy the newly trained model"""
        from app import current_app
        current_app.ai_model = self.trainer.model
        logger.info("New model deployed successfully")
        
        # Save the updated model
        self.trainer.model.save('ai/models/production/')