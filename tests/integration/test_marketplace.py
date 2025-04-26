import pytest
from deriv.models import User, Strategy, UserStrategy

def test_strategy_purchase(client, db, auth):
    """Test purchasing a strategy"""
    # Create a test user and log in
    auth.register()
    auth.login()
    
    # Create a test strategy
    strategy = Strategy(
        name='Test Strategy',
        description='A test strategy',
        code='def analyze(): pass',
        price=10.00,
        is_public=True,
        creator_id=1
    )
    db.session.add(strategy)
    db.session.commit()
    
    # Purchase the strategy
    response = client.post(f'/marketplace/purchase/{strategy.id}', follow_redirects=True)
    assert response.status_code == 200
    
    # Verify the purchase was recorded
    purchase = UserStrategy.query.filter_by(user_id=1, strategy_id=strategy.id).first()
    assert purchase is not None

def test_strategy_creation(client, db, auth):
    """Test creating a new strategy"""
    # Create a test user and log in
    auth.register()
    auth.login()
    
    # Submit strategy creation form
    response = client.post('/marketplace/create', data={
        'name': 'New Strategy',
        'description': 'A new test strategy',
        'code': 'def analyze(): pass',
        'price': 15.00,
        'category': 'trend',
        'is_public': True
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify the strategy was created
    strategy = Strategy.query.filter_by(name='New Strategy').first()
    assert strategy is not None
    assert strategy.creator_id == 1