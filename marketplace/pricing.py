def calculate_price(base_price, strategy_type, complexity):
    """Calculate final price based on strategy type and complexity"""
    multipliers = {
        'trend': 1.2,
        'reversal': 1.5,
        'scalping': 1.8,
        'news': 2.0
    }
    
    complexity_factors = {
        'low': 1.0,
        'medium': 1.5,
        'high': 2.0
    }
    
    type_multiplier = multipliers.get(strategy_type.lower(), 1.0)
    complexity_factor = complexity_factors.get(complexity.lower(), 1.0)
    
    return base_price * type_multiplier * complexity_factor

def calculate_royalty(sale_price):
    """Calculate platform royalty (30%)"""
    return sale_price * 0.3

def calculate_author_earnings(sale_price):
    """Calculate author earnings (70% of sale price)"""
    return sale_price * 0.7