import pytest
from app import create_app
from config import TestingConfig
from app.extensions import db
from auth.models import User
from payments.models import Transaction, PaymentMethod
from bot.models import Trade

@pytest.fixture(scope='module')
def test_app():
    app = create_app(TestingConfig)
    with app.app_context():
        yield app

@pytest.fixture(scope='module')
def test_db(test_app):
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope='function')
def client(test_app, test_db):
    with test_app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def test_user(test_db):
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash='hashed_password',
        is_active=True
    )
    test_db.session.add(user)
    test_db.session.commit()
    return user

@pytest.fixture(scope='function')
def admin_user(test_db):
    user = User(
        username='admin',
        email='admin@example.com',
        password_hash='hashed_password',
        is_active=True,
        is_admin=True
    )
    test_db.session.add(user)
    test_db.session.commit()
    return user

@pytest.fixture(scope='function')
def test_transaction(test_db, test_user):
    transaction = Transaction(
        user_id=test_user.id,
        amount=100.0,
        currency='USD',
        provider='stripe',
        transaction_id='test_txn_123',
        status='completed'
    )
    test_db.session.add(transaction)
    test_db.session.commit()
    return transaction

@pytest.fixture(scope='function')
def test_trade(test_db, test_user):
    trade = Trade(
        user_id=test_user.id,
        symbol='EURUSD',
        amount=50.0,
        profit=5.0,
        status='won',
        strategy='trend_following'
    )
    test_db.session.add(trade)
    test_db.session.commit()
    return trade