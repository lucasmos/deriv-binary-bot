#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from random import randint, uniform, choice

from deriv import create_app, db
from deriv.models import User, Strategy, UserStrategy, TradeHistory

def load_fixtures():
    app = create_app()
    with app.app_context():
        # Create test users
        users = []
        for i in range(1, 6):
            user = User(
                username=f'testuser{i}',
                email=f'test{i}@example.com',
                created_at=datetime.utcnow() - timedelta(days=randint(1, 30))
            user.set_password('password')
            db.session.add(user)
            users.append(user)
            
        # Create test strategies
        strategies = []
        strategy_names = [
            'Trend Following Pro',
            'Mean Reversion',
            'Breakout Trader',
            'Scalping Master',
            'News Trader'
        ]
        
        for i, name in enumerate(strategy_names):
            strategy = Strategy(
                name=name,
                description=f'A {name.lower()} strategy',
                code=f'def analyze():\n    return {{"signal": "buy"}}',
                price=uniform(10, 50),
                is_public=True,
                creator_id=users[i % len(users)].id,
                created_at=datetime.utcnow() - timedelta(days=randint(1, 30)),
                download_count=randint(0, 100)
            )
            db.session.add(strategy)
            strategies.append(strategy)
        
        # Create purchases
        for user in users:
            for strategy in strategies:
                if randint(0, 1):  # 50% chance to purchase
                    purchase = UserStrategy(
                        user_id=user.id,
                        strategy_id=strategy.id,
                        purchased_at=datetime.utcnow() - timedelta(days=randint(0, 29))
                    db.session.add(purchase)
        
        # Create trade history
        symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
        for user in users:
            for _ in range(randint(10, 50)):
                trade = TradeHistory(
                    user_id=user.id,
                    symbol=choice(symbols),
                    direction=choice(['buy', 'sell']),
                    amount=round(uniform(5, 100), 2),
                    profit=round(uniform(-20, 20), 2),
                    timestamp=datetime.utcnow() - timedelta(days=randint(0, 29))
                )
                db.session.add(trade)
        
        db.session.commit()
        print("Fixtures loaded successfully")

if __name__ == '__main__':
    load_fixtures()