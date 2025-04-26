import pytest
from bot.brokers import DerivBroker, IQOptionBroker, BrokerFactory
from config import TestingConfig

class TestBrokersIntegration:
    @pytest.fixture
    def deriv_broker(self):
        return DerivBroker(TestingConfig.DERIV_API_KEY, TestingConfig.DERIV_ACCOUNT_ID)

    @pytest.fixture
    def iqoption_broker(self):
        return IQOptionBroker(TestingConfig.IQOPTION_EMAIL, TestingConfig.IQOPTION_PASSWORD)

    def test_deriv_broker_connection(self, deriv_broker, mocker):
        mocker.patch('bot.brokers.deriv.requests.get', return_value=MockResponse(200, {'balance': 1000.0}))
        balance = deriv_broker.get_balance()
        assert balance == 1000.0

    def test_iqoption_login(self, iqoption_broker, mocker):
        mocker.patch('bot.brokers.iqoption.IQOptionAPI.connect', return_value=True)
        assert iqoption_broker.login() is True

    def test_broker_factory(self):
        deriv = BrokerFactory.create_broker('deriv')
        assert isinstance(deriv, DerivBroker)
        
        iqoption = BrokerFactory.create_broker('iqoption')
        assert isinstance(iqoption, IQOptionBroker)

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data