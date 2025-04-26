from flask import Blueprint
from .services import PaymentService

payments_bp = Blueprint('payments', __name__, template_folder='templates')

# Initialize payment service with default provider
payment_service = PaymentService()

from . import routes