from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AirtelAuthRequest(BaseModel):
    client_id: str
    client_secret: str
    grant_type: str = "client_credentials"

class AirtelAuthResponse(BaseModel):
    access_token: str
    expires_in: int
    token_type: str

class AirtelSubscriber(BaseModel):
    country: str = "KE"
    currency: str = "KES"
    msisdn: str

class AirtelTransaction(BaseModel):
    amount: float
    country: str = "KE"
    currency: str = "KES"
    id: str

class AirtelPaymentRequest(BaseModel):
    reference: str
    subscriber: AirtelSubscriber
    transaction: AirtelTransaction

class AirtelPaymentResponse(BaseModel):
    status: dict
    data: dict
    transaction: Optional[dict]
    airtel_money_id: Optional[str] = Field(None, alias="airtel_money_id")

class AirtelWebhookPayload(BaseModel):
    transaction: dict
    payment: dict
    timestamp: datetime