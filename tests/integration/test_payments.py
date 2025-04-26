import pytest
from payments.services import PaymentService
from payments.providers import StripePaymentProvider, AirtelPaymentProvider

class TestPaymentsIntegration:
    @pytest.fixture
    def payment_service(self):
        return PaymentService()

    def test_stripe_payment_processing(self, payment_service, mocker):
        mocker.patch('stripe.PaymentIntent.create', return_value={
            'id': 'pi_test123',
            'status': 'succeeded',
            'amount_received': 10000
        })
        
        result = payment_service.process_deposit(
            1, 100.0, 'USD', 'stripe', 'pm_test123'
        )
        assert result['success'] is True
        assert result['transaction_id'] == 'pi_test123'

    def test_airtel_payment_processing(self, payment_service, mocker):
        mocker.patch('payments.providers.airtel.client.AirtelPaymentProvider._get_auth_token', return_value='test_token')
        mocker.patch('requests.post', return_value=MockResponse(200, {
            'data': {'transaction': {'id': 'airtel_test123'}}
        }))
        
        result = payment_service.process_deposit(
            1, 100.0, 'KES', 'airtel', '254712345678'
        )
        assert result['success'] is True
        assert 'airtel_test123' in result['transaction_id']

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data