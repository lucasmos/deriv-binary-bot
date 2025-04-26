import os
import pytest
from deriv import create_app, db as _db
from deriv.config import TestConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    
    with app.app_context():
        _db.create_all()
        
    yield app
    
    # Clean up after the test
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Provide the transactional fixtures with access to the database."""
    with app.app_context():
        _db.init_app(app)
        yield _db
        _db.session.remove()