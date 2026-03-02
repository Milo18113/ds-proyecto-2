from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.implementations import (
    SqlCustomerRepository,
    SqlAccountRepository,
    SqlTransactionRepository,
    SqlLedgerRepository,
)
from app.application.banking_facade import BankingFacade
from app.application.dtos import (
    CustomerCreate,
    CustomerResponse,
    AccountCreate,
    AccountResponse,
    AccountDeposit,
    AccountWithdraw,
    TransferRequest,
    TransactionResponse,
    TransactionHistoryResponse,
)
from app.domain.strategies.fee_strategy import PercentFeeStrategy
from app.domain.strategies.risk_strategy import MaxAmountRule, VelocityRule, DailyLimitRule
from app.domain.exceptions import (
    DomainError,
    AccountNotFound,
    CustomerNotFound,
    InsufficientFundsError,
    RiskRejectedError,
)

router = APIRouter()


def get_facade(db: Session = Depends(get_db)) -> BankingFacade:
    return BankingFacade(
        customer_repository=SqlCustomerRepository(db),
        account_repository=SqlAccountRepository(db),
        transaction_repository=SqlTransactionRepository(db),
        ledger_repository=SqlLedgerRepository(db),
        fee_strategy=PercentFeeStrategy(0.015),
        risk_rules=[
            MaxAmountRule(max_amount=10000),
            VelocityRule(max_transactions=10),
            DailyLimitRule(daily_limit=50000),
        ],
    )


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/customers", response_model=CustomerResponse)
def create_customer(dto: CustomerCreate, facade: BankingFacade = Depends(get_facade)):
    try:
        customer = facade.create_customer(name=dto.name, email=dto.email)
        return CustomerResponse(
            id=str(customer.id), name=customer.name,
            email=customer.email, status=customer.status,
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/accounts", response_model=AccountResponse)
def create_account(dto: AccountCreate, facade: BankingFacade = Depends(get_facade)):
    try:
        account = facade.create_account(
            customer_id=dto.customer_id, currency=dto.currency,
        )
        return AccountResponse(
            id=str(account.id), customer_id=account.customer_id,
            currency=account.currency, balance=account.balance,
            status=account.status,
        )
    except CustomerNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, facade: BankingFacade = Depends(get_facade)):
    try:
        account = facade.get_account(account_id)
        return AccountResponse(
            id=account.id, customer_id=account.customer_id,
            currency=account.currency, balance=account.balance,
            status=account.status,
        )
    except AccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/transactions/deposit", response_model=TransactionResponse)
def deposit(dto: AccountDeposit, facade: BankingFacade = Depends(get_facade)):
    try:
        tx = facade.deposit(account_id=dto.account_id, amount=dto.amount)
        return TransactionResponse(
            id=tx.id, type=tx.type, amount=tx.amount,
            currency=tx.currency, status=tx.status,
        )
    except (AccountNotFound,) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (RiskRejectedError, InsufficientFundsError, DomainError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/withdraw", response_model=TransactionResponse)
def withdraw(dto: AccountWithdraw, facade: BankingFacade = Depends(get_facade)):
    try:
        tx = facade.withdraw(account_id=dto.account_id, amount=dto.amount)
        return TransactionResponse(
            id=tx.id, type=tx.type, amount=tx.amount,
            currency=tx.currency, status=tx.status,
        )
    except (AccountNotFound,) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (RiskRejectedError, InsufficientFundsError, DomainError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transactions/transfer", response_model=TransactionResponse)
def transfer(dto: TransferRequest, facade: BankingFacade = Depends(get_facade)):
    try:
        tx = facade.transfer(
            from_account_id=dto.from_account_id,
            to_account_id=dto.to_account_id,
            amount=dto.amount,
        )
        return TransactionResponse(
            id=tx.id, type=tx.type, amount=tx.amount,
            currency=tx.currency, status=tx.status,
        )
    except (AccountNotFound,) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (RiskRejectedError, InsufficientFundsError, DomainError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_id}/transactions", response_model=TransactionHistoryResponse)
def list_transactions(account_id: str, facade: BankingFacade = Depends(get_facade)):
    try:
        facade.get_account(account_id)
        transactions = facade.list_transactions(account_id)
        return TransactionHistoryResponse(
            account_id=account_id,
            transactions=[
                TransactionResponse(
                    id=tx.id, type=tx.type, amount=tx.amount,
                    currency=tx.currency, status=tx.status,
                )
                for tx in transactions
            ],
            total_count=len(transactions),
        )
    except AccountNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))