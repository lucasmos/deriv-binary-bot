from datetime import datetime
import numpy as np
from bot.utils.error_handler import ErrorHandler
from bot.analysis.market_analyzer import MarketConditionAnalyzer
from bot.analysis.winloss_simulator import WinLossSimulator

class DemoAccountService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.initial_balance = 10000.00
        self.current_balance = self.initial_balance
        self.trade_history = []
        self.winloss_simulator = WinLossSimulator()
        self.market_analyzer = MarketConditionAnalyzer()
        self.error_handler = ErrorHandler('DemoAccountService')
        
    @ErrorHandler.handle_recoverable
    def execute_trade(self, symbol, contract_type, amount, duration, prediction=None):
        """Execute a simulated trade with realistic market conditions"""
        if amount > self.current_balance:
            raise ValueError("Insufficient demo balance")
        
        # Get realistic win probability
        win_prob = self.winloss_simulator.get_win_probability(
            symbol=symbol,
            contract_type=contract_type,
            time_frame=f"{duration}m"
        )
        
        # Adjust with AI prediction if available
        if prediction:
            ai_prob = prediction.get('buy' if contract_type == 'CALL' else 'sell', 0.5)
            win_prob = (win_prob * 0.6) + (ai_prob * 0.4)  # Weighted average
        
        # Current market sentiment adjustment
        sentiment = self.market_analyzer.get_current_sentiment(symbol)
        if (sentiment == 'bullish' and contract_type == 'CALL') or \
           (sentiment == 'bearish' and contract_type == 'PUT'):
            win_prob *= 1.05
        
        # Random factor (1-3%)
        final_prob = win_prob * np.random.uniform(0.98, 1.02)
        
        # Generate outcome
        is_win = np.random.random() < final_prob
        payout_pct = self._get_payout_percentage(symbol, duration)
        payout = amount * payout_pct if is_win else -amount
        
        # Update balance
        self.current_balance += payout
        if self.current_balance < 0:
            self.current_balance = 0
        
        # Record trade
        trade_record = {
            'timestamp': datetime.utcnow(),
            'symbol': symbol,
            'contract_type': contract_type,
            'amount': amount,
            'duration': duration,
            'payout': payout,
            'result': 'win' if is_win else 'loss',
            'balance': self.current_balance,
            'prediction_used': prediction,
            'win_probability': final_prob
        }
        
        self.trade_history.append(trade_record)
        return trade_record
    
    def _get_payout_percentage(self, symbol, duration):
        """Get realistic payout percentage based on asset and duration"""
        base_payout = {
            'forex': 0.78,
            'indices': 0.82,
            'commodities': 0.75
        }
        
        asset_type = 'forex' if symbol in self.winloss_simulator.base_win_rates['forex'] else \
                    'indices' if symbol in self.winloss_simulator.base_win_rates['indices'] else 'commodities'
        
        # Shorter durations typically have lower payouts
        duration_factor = 0.8 + (0.2 * (min(duration, 15) / 15))
        
        return base_payout[asset_type] * duration_factor * np.random.uniform(0.95, 1.0)
    
    def reset_balance(self):
        """Reset demo balance to initial amount"""
        self.current_balance = self.initial_balance
        return True
    
    def get_trade_history(self, limit=100):
        """Get recent trade history"""
        return sorted(self.trade_history, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def get_performance_stats(self):
        """Calculate trading performance metrics"""
        if not self.trade_history:
            return None
            
        wins = sum(1 for trade in self.trade_history if trade['result'] == 'win')
        losses = len(self.trade_history) - wins
        win_rate = (wins / len(self.trade_history)) * 100 if self.trade_history else 0
        profit = sum(trade['payout'] for trade in self.trade_history)
        
        return {
            'total_trades': len(self.trade_history),
            'wins': wins,
            'losses': losses,
            'win_rate': f"{win_rate:.2f}%",
            'total_profit': f"${profit:.2f}",
            'current_balance': f"${self.current_balance:.2f}"
        }