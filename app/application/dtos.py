from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.domain.enums import AccountStatus, Direction, TransactionStatus, TransactionType


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    status: str


class AccountCreate(BaseModel):
    customer_id: str
    currency: str = "USD"

class AccountResponse(BaseModel):
    id: str
    customer_id: str
    currency: str
    balance: float
    status: AccountStatus


class AccountDeposit(BaseModel):
    account_id: str
    amount: float = Field(..., gt=0)

class AccountWithdraw(BaseModel):
    account_id: str
    amount: float = Field(..., gt=0)


class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(..., gt=0)


class TransactionResponse(BaseModel):
    id: str
    type: TransactionType
    amount: float
    currency: str
    status: TransactionStatus


class LedgerEntryResponse(BaseModel):
    id: str
    account_id: str
    transaction_id: str
    direction: Direction
    amount: float


class TransactionHistoryResponse(BaseModel):
    account_id: str
    transactions: List[TransactionResponse]
    total_count: int


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None