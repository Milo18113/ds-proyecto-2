from typing import List
import uuid
from app.domain.factories.transaction_factory import TransactionFactory
from app.domain.factories.ledger_entry_factory import LedgerEntryFactory
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction
from app.domain.exceptions import AccountNotFound
from app.repositories.interfaces import AccountRepository, CustomerRepository, TransactionRepository, LedgerRepository

class AccountService:
    def __init__(self, account_repo: AccountRepository, 
                 customer_repo: CustomerRepository,
                 transaction_repo: TransactionRepository,
                 ledger_repo: LedgerRepository):
        self.account_repo = account_repo
        self.customer_repo = customer_repo
        self.transaction_repo = transaction_repo
        self.ledger_repo = ledger_repo

    def create_account(self, customer_id: str, currency: str, initial_balance: float = 0.0, status: str = "ACTIVE") -> Account:
        # Business logic for account creation
        self._validate_account_creation(customer_id, currency, initial_balance)
        
        # Check if customer exists and is active
        customer = self.customer_repo.get_by_id(customer_id)  # You'll need customer_repo reference
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        if customer.status != "ACTIVE":
            raise ValueError(f"Cannot create account for inactive customer {customer_id}")
        
        # Check customer's existing accounts (business rules)
        existing_accounts = self.account_repo.get_by_customer_id(customer_id)
        if len(existing_accounts) >= 5:  # Example: max 5 accounts per customer
            raise ValueError(f"Customer {customer_id} already has maximum number of accounts")
        
        # Create account
        account = Account(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            currency=currency,
            balance=initial_balance,
            status=status
        )
        
        return self.account_repo.save(account)

    def _validate_account_creation(self, customer_id: str, currency: str, initial_balance: float):
        # Business validation rules
        if currency not in ["USD", "EUR", "CAD", "GBP"]:
            raise ValueError(f"Unsupported currency: {currency}")
        
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        
        if initial_balance > 1000000:  # Example: large opening deposit requires review
            raise ValueError("Initial balance exceeds maximum allowed amount")
    
    def get_account(self, account_id: str) -> Account:
        return self.account_repo.get_by_id(account_id)
    
    def process_deposit(self, account_id: str, amount: float) -> Transaction:
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise AccountNotFound(f"Account {account_id} not found")
        
        # Calculate fees
        fee_amount = self._calculate_transaction_fee(amount, "DEPOSIT")
        net_amount = amount - fee_amount
        
        # Risk checks
        self._validate_deposit_limits(account, net_amount)
        
        # Process transaction
        transaction = self._create_deposit_transaction(net_amount, fee_amount)
        account.deposit(net_amount)
        
        # Save everything
        self.account_repo.save(account)
        self.transaction_repo.save(transaction)
        self.ledger_repo.save(self._create_ledger_entry(account_id, transaction.id, "CREDIT", net_amount))
        
        return transaction

    def _calculate_transaction_fee(self, amount: float, transaction_type: str) -> float:
        # Business rules for fees
        if transaction_type == "DEPOSIT":
            return 0.0  # No fee for deposits
        elif transaction_type == "WITHDRAW":
            return min(amount * 0.02, 5.0)  # 2% or $5 max
        elif transaction_type == "TRANSFER":
            return min(amount * 0.01, 10.0)  # 1% or $10 max
        return 0.0
    
    def _validate_deposit_limits(self, account: Account, amount: float):
        # Business rules: daily limits, suspicious activity, etc.
        if amount > 10000:  
            raise ValueError("Deposit exceeds daily limit")
    
    def _create_deposit_transaction(self, amount: float) -> Transaction:
        return TransactionFactory.create("DEPOSIT", amount, "USD")
    
    def _create_ledger_entry(self, account_id: str, transaction_id: str, direction: str, amount: float):
        return LedgerEntryFactory.create(account_id, transaction_id, direction, amount)