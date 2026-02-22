import uuid

from fastapi import Depends
from sqlalchemy.orm import Session
from app.application.dtos import AccountCreate, AccountDeposit, AccountWithdraw, CustomerCreate, TransferRequest
from app.domain.entities import account
from app.domain.entities.account import Account
from app.domain.entities.customer import Customer
from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.entities.transaction import Transaction
from app.domain.exceptions import AccountNotFound
from app.domain.factories.ledger_entry_factory import LedgerEntryFactory
from app.domain.factories.transaction_factory import TransactionFactory
from app.domain.enums import Direction, TransactionType
from app.repositories.implementations import SqlAccountRepository, SqlCustomerRepository, SqlLedgerRepository, SqlTransactionRepository
from app.services.account_service import AccountService
from app.services.customer_service import CustomerService
from app.services.transaction_ledger_service import TransactionLedgerService
from app.repositories.database import get_db


# Dependencies

def get_account_service(db: Session = Depends(get_db)) -> AccountService:
    return AccountService(
        account_repo=SqlAccountRepository(db),
        transaction_repo=SqlTransactionRepository(db),
        ledger_repo=SqlLedgerRepository(db)
    )

def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(
        customer_repo=SqlCustomerRepository(db),
        account_repo=SqlAccountRepository(db)
    )

def get_transaction_ledger_service(db: Session = Depends(get_db)) -> TransactionService:
    return TransactionLedgerService(
        transaction_repo=SqlTransactionRepository(db),
        ledger_repo=SqlLedgerRepository(db)
    )


 
def get_banking_facade(account_service: AccountService = Depends(get_account_service),
                     customer_service: CustomerService = Depends(get_customer_service),
                     transaction_ledger_service: TransactionLedgerService = Depends(get_transaction_ledger_service)) -> 'BankingFacade':
    return BankingFacade(
        bank_currency="USD",
        customer_service=customer_service,
        account_service=account_service,
        transaction_ledger_service=transaction_ledger_service
    )

class BankingFacade:
    def __init__(self, bank_currency: str, 
                 customer_service: CustomerService,
                 account_service: AccountService,
                 transaction_ledger_service: TransactionLedgerService):
        self.bank_currency = bank_currency      # Single for the whole bank
        self.customer_service = customer_service
        self.account_service = account_service
        self.transaction_ledger_service = transaction_ledger_service

    # Create, Get Entities

    def create_customer(self, customer_dto: CustomerCreate):
        return self.customer_service.create_customer(
            customer_dto.name, 
            customer_dto.email, 
            customer_dto.status
        )

    def get_customer(self, customer_id: str) -> Customer:
        return self.customer_service.get_customer(customer_id)

    def create_account(self, account_dto: AccountCreate):
        account = Account.create_from_dto(account_dto)
        self.account_service.create_account(
            account_dto.customer_id,
            account_dto.currency,
            account_dto.balance,
            account_dto.status
        )
        return account

    def get_account(self, account_id: str) -> Account:
        return self.account_service.get_account(account_id)

    def get_transaciton(self, transaction_id: str) -> Transaction:
        return self.transaction_ledger_service.get_transaction(transaction_id)

    def list_transactions(self, account_id: str):
        return self.transaction_ledger_service.list_transactions_by_account(account_id)
        

    # Create Transactions

    def deposit(self, deposit_dto: AccountDeposit) -> Transaction:
        account = self.get_account(deposit_dto.id)
        if account is None:
            raise AccountNotFound(f"No se encontró la cuenta con id {deposit_dto.id}")

        transaction = TransactionFactory.create(
            TransactionType.DEPOSIT, deposit_dto.amount, self.bank_currency)

        account.deposit(transaction.amount)
        self.transaction_ledger_service.save_transaction(transaction)

        # Create ledger entry
        self.transaction_ledger_service.save_ledger_entry(LedgerEntryFactory.create(
            account_id=account.id,
            transaction_id=transaction.id, 
            direction=Direction.CREDIT,
            amount=transaction.amount
        ))

        return transaction

    def withdraw(self, withdraw_dto: AccountWithdraw) -> Transaction:
        account = self.get_account(withdraw_dto.id)
        if account is None:
            raise AccountNotFound(f"No se encontró la cuenta con id {withdraw_dto.id}")

        transaction = TransactionFactory.create(
            TransactionType.WITHDRAW, withdraw_dto.amount, self.bank_currency)

        account.withdraw(transaction.amount)
        self.transaction_ledger_service.save_transaction(transaction)

        # Create ledger entry
        self.transaction_ledger_service.save_ledger_entry(LedgerEntryFactory.create(
            account_id=account.id,                
            transaction_id=transaction.id,
            direction=Direction.DEBIT,
            amount=transaction.amount
        ))

        return transaction

    def transfer(self, transfer_dto: TransferRequest) -> Transaction:
        from_account = self.get_account(transfer_dto.from_account_id)
        to_account = self.get_account(transfer_dto.to_account_id)

        transaction = TransactionFactory.create(
            TransactionType.TRANSFER, transfer_dto.amount, self.bank_currency)

        from_account.transfer(transaction.amount, to_account)
        self.transaction_ledger_service.save_transaction(transaction)

        # Create ledger entries
        self.transaction_ledger_service.save_ledger_entry(LedgerEntryFactory.create(
            account_id=from_account.id,                
            transaction_id=transaction.id,
            direction=Direction.DEBIT,
            amount=transaction.amount
        ))
        self.transaction_ledger_service.save_ledger_entry(LedgerEntryFactory.create(
            account_id=to_account.id,                
            transaction_id=transaction.id,
            direction=Direction.CREDIT,
            amount=transaction.amount
        ))
        
        return transaction

    
    # Get Ledger Entries

    def get_ledger_entries(self, account_id: str):
        return self.transaction_ledger_service.get_ledger_entries_by_account(account_id)

    def get_ledger_entries(self, transaction_id: str):
        return self.transaction_ledger_service.get_ledger_entries_by_transaction(transaction_id)