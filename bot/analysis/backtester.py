import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils import TechnicalIndicators
from ..strategies import StrategyFactory

class Backtester:
    def __init__(self, config):
        self.config = config
        self.indicators = TechnicalIndicators()
        self.strategy_factory = StrategyFactory(config)
        
    def backtest_strategy(self, strategy_name, historical_data, initial_balance=10000):
        """Backtest a trading strategy on historical data"""
        strategy = self.strategy_factory.get_strategy(strategy_name)
        df = pd.DataFrame(historical_data)
        
        # Convert timestamp if needed
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
        
        # Generate signals
        df['signal'] = 0
        for i in range(1, len(df)):
            data_window = df.iloc[max(0, i-100):i].to_dict('records')
            signal = strategy.generate_signal(data_window)
            if signal:
                df.at[df.index[i], 'signal'] = 1 if signal['direction'] == 'buy' else -1
        
        # Calculate returns
        df['returns'] = df['close'].pct_change() * df['signal'].shift(1)
        df['cumulative_returns'] = (1 + df['returns']).cumprod()
        df['equity'] = initial_balance * df['cumulative_returns']
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(df, initial_balance)
        
        return {
            'equity_curve': df['equity'].to_list(),
            'dates': df.index.strftime('%Y-%m-%d').to_list(),
            'metrics': metrics
        }
        
    def _calculate_metrics(self, df, initial_balance):
        """Calculate performance metrics from backtest results"""
        total_trades = df['signal'].abs().sum()
        winning_trades = (df['returns'] > 0).sum()
        losing_trades = (df['returns'] < 0).sum()
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate max drawdown
        df['peak'] = df['equity'].cummax()
        df['drawdown'] = (df['equity'] - df['peak']) / df['peak']
        max_drawdown = df['drawdown'].min()
        
        return {
            'initial_balance': initial_balance,
            'final_balance': df['equity'].iloc[-1],
            'total_trades': total_trades,
            'win_rate': win_rate,
            'max_drawdown': max_drawdown,
            'profit_factor': abs(df[df['returns'] > 0]['returns'].sum() / 
                               df[df['returns'] < 0]['returns'].sum()) if losing_trades > 0 else float('inf')
        }