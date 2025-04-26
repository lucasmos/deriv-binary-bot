class RiskManager:
    def __init__(self, config):
        self.config = config
        self.max_risk_per_trade = config.get('MAX_RISK_PER_TRADE', 0.02)  # 2% of account
        self.max_daily_loss = config.get('MAX_DAILY_LOSS', 0.05)  # 5% of account
        self.risk_multipliers = {
            'high': 0.5,
            'medium': 1.0,
            'low': 1.5
        }
        
    def calculate_position_size(self, account_balance, volatility='medium'):
        """Calculate position size based on account balance and volatility"""
        base_risk = account_balance * self.max_risk_per_trade
        adjusted_risk = base_risk * self.risk_multipliers.get(volatility, 1.0)
        return adjusted_risk
        
    def assess_trade_risk(self, trade_data, account_data):
        """Comprehensive trade risk assessment"""
        # Check daily loss limits
        if account_data['daily_pnl'] <= -abs(account_data['balance'] * self.max_daily_loss):
            return False, "Daily loss limit reached"
            
        # Check position concentration
        open_positions_value = sum(
            pos['amount'] for pos in account_data['open_positions']
        )
        if open_positions_value > account_data['balance'] * 0.3:  # 30% exposure
            return False, "Position concentration too high"
            
        return True, "Risk assessment passed"