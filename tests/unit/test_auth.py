import pytest
from deriv.models import User
from deriv.auth.forms import RegistrationForm, LoginForm

def test_new_user():
    """Test creating a new user"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('password')
    assert not user.check_password('wrongpassword')

def test_registration_form():
    """Test registration form validation"""
    form_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password',
        'confirm_password': 'password'
    }
    
    form = RegistrationForm(data=form_data)
    assert form.validate() is True
    
    # Test invalid email
    invalid_email_data = form_data.copy()
    invalid_email_data['email'] = 'invalid'
    form = RegistrationForm(data=invalid_email_data)
    assert form.validate() is False
    
    # Test password mismatch
    mismatch_data = form_data.copy()
    mismatch_data['confirm_password'] = 'different'
    form = RegistrationForm(data=mismatch_data)
    assert form.validate() is False

def test_login_form():
    """Test login form validation"""
    form_data = {
        'email': 'test@example.com',
        'password': 'password',
        'remember': True
    }
    
    form = LoginForm(data=form_data)
    assert form.validate() is True
    
    # Test missing email
    missing_email = form_data.copy()
    missing_email['email'] = ''
    form = LoginForm(data=missing_email)
    assert form.validate() is False