from enum import Enum

class BrokerType(Enum):
    DERIV = 'deriv'
    QUOTEX = 'quotex'
    IQOPTION = 'iqoption'
    POCKETOPTION = 'pocketoption'

class TradeDirection(Enum):
    CALL = 'CALL'
    PUT = 'PUT'

class Timeframe(Enum):
    M1 = '1m'
    M5 = '5m'
    M15 = '15m'
    H1 = '1h'
    D1 = '1d'

class PaymentProvider(Enum):
    MPESA = 'mpesa'
    AIRTEL = 'airtel'
    STRIPE = 'stripe'

class TransactionStatus(Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class StrategyCategory(Enum):
    FOREX = 'forex'
    CRYPTO = 'crypto'
    INDICES = 'indices'
    COMMODITIES = 'commodities'

# Risk levels
RISK_LEVELS = {
    'low': 0.01,    # 1% risk per trade
    'medium': 0.02, # 2% risk per trade
    'high': 0.05    # 5% risk per trade
}

# Trading hours
TRADING_SESSIONS = {
    'london': {'open': 8, 'close': 16},    # 8am-4pm GMT
    'new_york': {'open': 13, 'close': 21}, # 1pm-9pm GMT
    'tokyo': {'open': 0, 'close': 6},      # 12am-6am GMT
    'sydney': {'open': 22, 'close': 6}     # 10pm-6am GMT (next day)
}