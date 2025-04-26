import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ...bot.analysis.market_analyzer import MarketConditionAnalyzer

class SyntheticDataGenerator:
    def __init__(self):
        self.market_analyzer = MarketConditionAnalyzer()
        
    def generate_market_data(self, symbol, days=30, timeframe='1m'):
        """Generate synthetic market data for testing"""
        periods = days * 24 * 60  # Minutes in specified days
        if timeframe == '5m':
            periods = days * 24 * 12
        elif timeframe == '15m':
            periods = days * 24 * 4
        elif timeframe == '1h':
            periods = days * 24
        elif timeframe == '1d':
            periods = days
            
        base_price = np.random.uniform(50, 200)
        volatility = np.random.uniform(0.001, 0.02)
        
        # Generate random walk price series
        returns = np.random.normal(0, volatility, periods)
        prices = base_price * (1 + returns).cumprod()
        
        # Create DataFrame
        index = pd.date_range(
            end=datetime.now(),
            periods=periods,
            freq=timeframe
        )
        
        df = pd.DataFrame({
            'open': prices,
            'high': prices * np.random.uniform(1.0, 1.005, periods),
            'low': prices * np.random.uniform(0.995, 1.0, periods),
            'close': prices,
            'volume': np.random.lognormal(5, 1, periods)
        }, index=index)
        
        # Add technical indicators
        df = self.market_analyzer.add_technical_indicators(df)
        
        return df

def generate_synthetic_data(symbols, days=30, timeframe='1m'):
    """Generate synthetic datasets for multiple symbols"""
    generator = SyntheticDataGenerator()
    datasets = {}
    
    for symbol in symbols:
        datasets[symbol] = generator.generate_market_data(
            symbol, days, timeframe
        )
        
    return datasets