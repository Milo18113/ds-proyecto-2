import uuid
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


class BankingFacade:
    def __init__(self, bank_currency: str, 
                 customer_repository: SqlCustomerRepository,
                 account_repository: SqlAccountRepository,
                 transaction_repository: SqlTransactionRepository,
                 ledger_repository: SqlLedgerRepository):
        self.bank_currency = bank_currency  # single for the whole bank
        self.customer_repository = customer_repository
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.ledger_repository = ledger_repository

    # Create, Get Entities

    def create_customer(self, customer_dto: CustomerCreate):
        customer = Customer.create_from_dto(customer_dto)
        self.customer_repository.save(customer)
        return customer

    def get_customer(self, customer_id: str) -> Customer:
        return self.customer_repository.get_by_id(customer_id)

    def create_account(self, account_dto: AccountCreate):
        account = Account.create_from_dto(account_dto)
        self.account_repository.save(account)
        return account

    def get_account(self, account_id: str) -> Account:
        return self.account_repository.get_by_id(account_id)

    def get_transaciton(self, transaction_id: str) -> Transaction:
        return self.transaction_repository.get_by_id(transaction_id)

    def list_transactions(self, account_id: str):
        return self.transaction_repository.get_by_account_id(account_id)
        

    # Create Transactions

    def deposit(self, deposit_dto: AccountDeposit) -> Transaction:
        account = self.get_account(deposit_dto.id)
        if account is None:
            raise AccountNotFound(f"No se encontró la cuenta con id {deposit_dto.id}")

        transaction = TransactionFactory.create(
            TransactionType.DEPOSIT, deposit_dto.amount, self.bank_currency)

        account.deposit(transaction.amount)
        self.transaction_repository.save(transaction)

        # Create ledger entry
        self.ledger_repository.save(LedgerEntryFactory.create(
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
        self.transaction_repository.save(transaction)

        # Create ledger entry
        self.ledger_repository.save(LedgerEntryFactory.create(
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
        self.transaction_repository.save(transaction)

        # Create ledger entries
        self.ledger_repository.save(LedgerEntryFactory.create(
            account_id=from_account.id,                
            transaction_id=transaction.id,
            direction=Direction.DEBIT,
            amount=transaction.amount
        ))
        self.ledger_repository.save(LedgerEntryFactory.create(
            account_id=to_account.id,                
            transaction_id=transaction.id,
            direction=Direction.CREDIT,
            amount=transaction.amount
        ))
        
        return transaction

    
    # Get Ledger Entries

    def get_ledger_entries(self, account_id: str):
        return self.ledger_repository.get_by_account_id(account_id)

    def get_ledger_entries(self, transaction_id: str):
        return self.ledger_repository.get_by_transaction_id(transaction_id)