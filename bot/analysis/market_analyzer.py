import pandas as pd
from ..utils import TechnicalIndicators

class MarketAnalyzer:
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators()
        
    def analyze_market_conditions(self, market_data):
        """Analyze current market conditions"""
        df = pd.DataFrame(market_data)
        
        # Calculate volatility
        df['returns'] = df['close'].pct_change()
        volatility = df['returns'].std() * (252 ** 0.5)  # Annualized volatility
        
        # Calculate trend strength
        df['sma_50'] = self.indicators.sma(df['close'], 50)
        df['sma_200'] = self.indicators.sma(df['close'], 200)
        trend_strength = abs(df['close'].iloc[-1] - df['sma_50'].iloc[-1]) / df['sma_50'].iloc[-1]
        
        # Determine market regime
        if df['sma_50'].iloc[-1] > df['sma_200'].iloc[-1]:
            market_regime = 'bullish'
        else:
            market_regime = 'bearish'
            
        # Calculate support/resistance levels
        support = df['low'].rolling(20).min().iloc[-1]
        resistance = df['high'].rolling(20).max().iloc[-1]
        
        return {
            'volatility': volatility,
            'trend_strength': trend_strength,
            'market_regime': market_regime,
            'support_level': support,
            'resistance_level': resistance,
            'current_price': df['close'].iloc[-1]
        }