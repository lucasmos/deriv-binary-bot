import pytest
import time
from datetime import datetime, timedelta
from bot.utils.time_utils import TimeUtils
from bot.utils.data_utils import DataUtils
from auth.utils import generate_verification_token, verify_token

class TestUtils:
    def test_time_utils(self):
        # Test timestamp conversion
        timestamp = TimeUtils.datetime_to_timestamp(datetime(2023, 1, 1))
        assert timestamp == 1672531200
        
        # Test time difference
        now = datetime.now()
        future = now + timedelta(minutes=5)
        diff = TimeUtils.time_difference(now, future)
        assert diff == 300  # 5 minutes in seconds

    def test_data_utils(self):
        data = [1, 2, 3, 4, 5]
        normalized = DataUtils.normalize(data)
        assert min(normalized) >= 0
        assert max(normalized) <= 1
        
        denormalized = DataUtils.denormalize(normalized, min(data), max(data))
        assert pytest.approx(denormalized) == data

    def test_auth_token(self, test_app):
        with test_app.app_context():
            email = 'test@example.com'
            token = generate_verification_token(email)
            assert token is not None
            
            # Test valid token
            verified_email = verify_token(token)
            assert verified_email == email
            
            # Test expired token
            expired_token = generate_verification_token(email, expiration=-1)
            assert verify_token(expired_token) is None