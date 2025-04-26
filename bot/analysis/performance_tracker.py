import pandas as pd
from datetime import datetime, timedelta

class PerformanceTracker:
    def __init__(self, config):
        self.config = config
        self.trade_history = []
        
    def record_trade(self, trade_data):
        """Record a completed trade"""
        self.trade_history.append(trade_data)
        
    def get_performance_metrics(self, period='all'):
        """Calculate performance metrics for a given period"""
        df = pd.DataFrame(self.trade_history)
        
        if not df.empty:
            # Filter by period
            if period != 'all':
                if period == 'day':
                    cutoff = datetime.now() - timedelta(days=1)
                elif period == 'week':
                    cutoff = datetime.now() - timedelta(weeks=1)
                elif period == 'month':
                    cutoff = datetime.now() - timedelta(days=30)
                else:
                    cutoff = datetime.now() - timedelta(days=int(period))
                    
                df = df[df['close_time'] >= cutoff]
                
            if not df.empty:
                # Calculate metrics
                total_trades = len(df)
                winning_trades = len(df[df['profit'] > 0])
                losing_trades = len(df[df['profit'] < 0])
                win_rate = winning_trades / total_trades if total_trades > 0 else 0
                avg_profit = df['profit'].mean()
                profit_factor = abs(df[df['profit'] > 0]['profit'].sum() / 
                                   abs(df[df['profit'] < 0]['profit'].sum())) if losing_trades > 0 else float('inf')
                
                return {
                    'total_trades': total_trades,
                    'winning_trades': winning_trades,
                    'losing_trades': losing_trades,
                    'win_rate': win_rate,
                    'avg_profit': avg_profit,
                    'profit_factor': profit_factor,
                    'net_profit': df['profit'].sum(),
                    'max_drawdown': self._calculate_drawdown(df)
                }
                
        return None
        
    def _calculate_drawdown(self, df):
        """Calculate maximum drawdown"""
        df = df.sort_values('close_time')
        df['cumulative'] = df['profit'].cumsum()
        df['peak'] = df['cumulative'].cummax()
        df['drawdown'] = df['peak'] - df['cumulative']
        return df['drawdown'].max()