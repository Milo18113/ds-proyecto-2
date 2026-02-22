from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import uuid4

router = APIRouter()

# =========================
# DTOs (stubs mínimos)
# =========================
class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    phone: Optional[str] = None
    id_number: Optional[str] = None


class CustomerOut(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    id_number: Optional[str] = None


class AccountCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    currency: str = Field(default="USD", min_length=1)


class AccountOut(BaseModel):
    id: str
    customer_id: str
    currency: str
    balance: float


class AmountRequest(BaseModel):
    account_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)


class TransferRequest(BaseModel):
    from_account_id: str = Field(..., min_length=1)
    to_account_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    note: Optional[str] = None


class TransactionOut(BaseModel):
    id: str
    type: str
    status: str
    amount: float
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    fee: float = 0.0
    note: Optional[str] = None


# =========================
# "DB" en memoria (solo para que Swagger/UI funcione)
# =========================
CUSTOMERS: Dict[str, CustomerOut] = {}
ACCOUNTS: Dict[str, AccountOut] = {}
TX_BY_ACCOUNT: Dict[str, List[TransactionOut]] = {}


def _push_tx(account_id: str, tx: TransactionOut) -> None:
    TX_BY_ACCOUNT.setdefault(account_id, []).insert(0, tx)


# =========================
# Healthcheck
# =========================
@router.get("/health")
def health():
    return {"status": "ok"}


# =========================
# Customers
# =========================
@router.post("/customers", response_model=CustomerOut)
def create_customer(payload: CustomerCreate):
    cid = str(uuid4())
    customer = CustomerOut(id=cid, **payload.model_dump())
    CUSTOMERS[cid] = customer
    return customer


# =========================
# Accounts
# =========================
@router.post("/accounts", response_model=AccountOut)
def create_account(payload: AccountCreate):
    if payload.customer_id not in CUSTOMERS:
        raise HTTPException(status_code=404, detail="Customer not found")

    aid = str(uuid4())
    account = AccountOut(
        id=aid,
        customer_id=payload.customer_id,
        currency=payload.currency,
        balance=0.0,
    )
    ACCOUNTS[aid] = account
    TX_BY_ACCOUNT.setdefault(aid, [])
    return account


@router.get("/accounts/{account_id}", response_model=AccountOut)
def get_account(account_id: str):
    acc = ACCOUNTS.get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc


@router.get("/accounts/{account_id}/transactions", response_model=List[TransactionOut])
def list_transactions(account_id: str):
    if account_id not in ACCOUNTS:
        raise HTTPException(status_code=404, detail="Account not found")
    return TX_BY_ACCOUNT.get(account_id, [])


# =========================
# Transactions (stubs)
# =========================
@router.post("/transactions/deposit", response_model=TransactionOut)
def deposit(payload: AmountRequest):
    acc = ACCOUNTS.get(payload.account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # simple: deposit always approved
    acc.balance += payload.amount

    tx = TransactionOut(
        id=str(uuid4()),
        type="DEPOSIT",
        status="APPROVED",
        amount=payload.amount,
        to_account_id=payload.account_id,
        fee=0.0,
    )
    _push_tx(payload.account_id, tx)
    return tx


@router.post("/transactions/withdraw", response_model=TransactionOut)
def withdraw(payload: AmountRequest):
    acc = ACCOUNTS.get(payload.account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    if acc.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    acc.balance -= payload.amount

    tx = TransactionOut(
        id=str(uuid4()),
        type="WITHDRAW",
        status="APPROVED",
        amount=payload.amount,
        from_account_id=payload.account_id,
        fee=0.0,
    )
    _push_tx(payload.account_id, tx)
    return tx


@router.post("/transactions/transfer", response_model=TransactionOut)
def transfer(payload: TransferRequest):
    from_acc = ACCOUNTS.get(payload.from_account_id)
    to_acc = ACCOUNTS.get(payload.to_account_id)
    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="Account not found")

    if from_acc.balance < payload.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # fee stub: 0.5% capped
    fee = min(payload.amount * 0.005, 5.0)

    total_debit = payload.amount + fee
    if from_acc.balance < total_debit:
        raise HTTPException(status_code=400, detail="Insufficient funds (including fee)")

    from_acc.balance -= total_debit
    to_acc.balance += payload.amount

    tx = TransactionOut(
        id=str(uuid4()),
        type="TRANSFER",
        status="APPROVED",
        amount=payload.amount,
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        fee=fee,
        note=payload.note,
    )
    _push_tx(payload.from_account_id, tx)
    _push_tx(payload.to_account_id, tx)
    return tx