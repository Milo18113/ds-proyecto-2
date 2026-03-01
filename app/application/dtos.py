from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from app.domain.enums import AccountStatus, Direction, TransactionStatus, TransactionType

# Customer DTOs
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    status: str = "ACTIVE"

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str = Field(None, pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    status: str

class CustomerUpdate(BaseModel):
    name: Optional[str]
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Account DTOs
class AccountCreate(BaseModel):
    customer_id: str
    currency: str = Field(..., min_length=3, max_length=3, regex=r"^USD|EUR|CAD|GBP$")
    balance: float = Field(0.0, ge=0)
    status: AccountStatus

class AccountResponse(BaseModel):
    id: str
    customer_id: str
    currency: str = Field(..., min_length=3, max_length=3, regex=r"^USD|EUR|CAD|GBP$")
    balance: float
    status: AccountStatus

class AccountUpdate(BaseModel):
    id: str
    status: AccountStatus

class AccountDeposit(BaseModel):
    id: str
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")

class AccountWithdraw(BaseModel):
    id: str
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")

# Transaction DTOs
class TransactionCreate(BaseModel):
    type: TransactionType
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    currency: str = Field(..., min_length=3, max_length=3, regex=r"^USD|EUR|CAD|GBP$")

class TransactionResponse(BaseModel):
    id: str
    type: TransactionType
    amount: float
    currency: str = Field(..., min_length=3, max_length=3, regex=r"^USD|EUR|CAD|GBP$")
    status: TransactionStatus

class TransactionUpdate(BaseModel):
    status: TransactionStatus

class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    currency: str = Field(..., min_length=3, max_length=3, regex=r"^USD|EUR|CAD|GBP$")

# Common Utility DTOs
class BalanceResponse(BaseModel):
    account_id: str
    balance: float
    currency: str
    status: AccountStatus

class LedgerEntryResponse(BaseModel):       # Only output
    id: str
    account_id: str
    transaction_id: str
    direction: Direction  # DEBIT or CREDIT
    amount: float

class TransactionHistoryResponse(BaseModel):
    account_id: str
    transactions: List[TransactionResponse]
    ledger_entries: List[LedgerEntryResponse] 
    total_count: int

class ErrorResponse(BaseModel):                     # ?? 
    error: str
    message: str
    details: Optional[dict] = None

# Additional useful DTOs
# class AccountSummaryResponse(BaseModel):
#     account: AccountResponse
#     recent_transactions: List[TransactionResponse]
#     balance: BalanceResponse

# class CustomerAccountsResponse(BaseModel):
#     customer: CustomerResponse
#     accounts: List[AccountResponse]
#     total_accounts: int