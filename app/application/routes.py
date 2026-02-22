from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.application.banking_facade import BankingFacade
from app.application.dtos import AccountCreate, AccountDeposit, AccountWithdraw, CustomerCreate, TransferRequest
from app.repositories.database import get_db
from app.repositories.implementations import (
    SqlCustomerRepository, 
    SqlAccountRepository, 
    SqlTransactionRepository,
    SqlLedgerRepository
)

router = APIRouter()

def get_banking_facade(db: Session = Depends(get_db)) -> BankingFacade:
    return BankingFacade(
        bank_currency="USD",
        customer_repository=SqlCustomerRepository(db),
        account_repository=SqlAccountRepository(db),
        transaction_repository=SqlTransactionRepository(db),
        ledger_repository=SqlLedgerRepository(db)
    )

@router.post("/customers")
async def create_customer(
    customer_dto: CustomerCreate,
    facade: BankingFacade = Depends(get_banking_facade) 
):
    customer = facade.create_customer(customer_dto)
    return customer

@router.post("/accounts")
async def create_account(
    account_dto: AccountCreate,
    facade: BankingFacade = Depends(get_banking_facade)
):
    account = facade.create_account(account_dto)
    return account

@router.get("/accounts/{account_id}")
async def get_account(
    account_id: str,
    facade: BankingFacade = Depends(get_banking_facade)
):
    account = facade.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.post("/transactions/deposit")
async def deposit_transaction(
    deposit_dto: AccountDeposit,
    facade: BankingFacade = Depends(get_banking_facade)
):
    transaction = facade.deposit(deposit_dto)
    return transaction

@router.post("/transactions/withdraw")
async def withdraw_transaction(
    withdraw_dto: AccountWithdraw,
    facade: BankingFacade = Depends(get_banking_facade)
):
    transaction = facade.withdraw(withdraw_dto)
    return transaction

@router.post("/transactions/transfer")
async def transfer_transaction(
    transfer_dto: TransferRequest,
    facade: BankingFacade = Depends(get_banking_facade)
):
    transaction = facade.transfer(transfer_dto)
    return transaction