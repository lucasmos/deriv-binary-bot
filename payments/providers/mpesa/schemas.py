from pydantic import BaseModel, Field
from typing import Optional

class MpesaAuthResponse(BaseModel):
    access_token: str
    expires_in: str

class MpesaSTKPushRequest(BaseModel):
    BusinessShortCode: str
    Password: str
    Timestamp: str
    TransactionType: str
    Amount: float
    PartyA: str
    PartyB: str
    PhoneNumber: str
    CallBackURL: str
    AccountReference: str
    TransactionDesc: str

class MpesaSTKPushResponse(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResponseCode: str
    ResponseDescription: str
    CustomerMessage: str

class MpesaCallbackItem(BaseModel):
    Name: str
    Value: Optional[str] = None

class MpesaCallbackMetadata(BaseModel):
    Item: list[MpesaCallbackItem]

class MpesaCallbackBody(BaseModel):
    stkCallback: dict

class MpesaCallback(BaseModel):
    Body: MpesaCallbackBody