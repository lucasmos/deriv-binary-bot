import numpy as np

class PositionSizer:
    def __init__(self, config):
        self.config = config
        self.max_risk_per_trade = config.get('MAX_RISK_PER_TRADE', 0.02)  # 2% of account
        
    def calculate(self, account_balance, stop_loss_pct, risk_per_trade=None):
        """
        Calculate position size based on account balance and stop loss percentage
        :param account_balance: Current account balance
        :param stop_loss_pct: Stop loss as percentage of entry price (e.g., 0.02 for 2%)
        :param risk_per_trade: Percentage of account to risk per trade (default from config)
        :return: Position size in currency amount
        """
        risk = risk_per_trade or self.max_risk_per_trade
        risk_amount = account_balance * risk
        position_size = risk_amount / stop_loss_pct
        
        # Apply rounding based on broker requirements
        return np.round(position_size, 2)
        
    def dynamic_sizing(self, account_balance, volatility_score, strategy_confidence):
        """
        Dynamic position sizing based on market conditions and strategy confidence
        :param volatility_score: 0-1, higher means more volatile
        :param strategy_confidence: 0-1, confidence in the strategy signal
        """
        base_size = self.calculate(account_balance, 0.02)  # 2% stop loss default
        
        # Adjust for volatility (higher volatility = smaller position)
        volatility_factor = 1 / (1 + volatility_score)  # volatility_score 0-1
        
        # Adjust for strategy confidence
        confidence_factor = strategy_confidence ** 2  # Square to emphasize high confidence
        
        final_size = base_size * volatility_factor * confidence_factor
        return np.round(final_size, 2)