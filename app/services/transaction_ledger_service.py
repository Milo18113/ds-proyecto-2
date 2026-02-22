import datetime
from typing import List, Optional
from app.domain.entities.transaction import Transaction
from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.exceptions import TransactionNotFound, AccountNotFound
from app.repositories.interfaces import TransactionRepository, LedgerRepository

class TransactionLedgerService:
    def __init__(self, transaction_repo: TransactionRepository, 
                 ledger_repo: LedgerRepository):
        self.transaction_repo = transaction_repo
        self.ledger_repo = ledger_repo
    
    def get_transaction(self, transaction_id: str) -> Transaction:
        transaction = self.transaction_repo.get_by_id(transaction_id)
        if not transaction:
            raise TransactionNotFound(f"Transaction {transaction_id} not found")
        return transaction
    
    def list_transactions_by_account(self, account_id: str) -> List[Transaction]:
        # Verify account exists
        account_transactions = self.transaction_repo.get_by_account_id(account_id)
        if not account_transactions:
            return []
        
        # Sort by date (newest first)
        return sorted(account_transactions, key=lambda x: x.created_at, reverse=True)
    
    def save_transaction(self, transaction: Transaction) -> Transaction:
        # Business validation before saving
        self._validate_transaction(transaction)
        return self.transaction_repo.save(transaction)
    
    def get_ledger_entries_by_account(self, account_id: str) -> List[LedgerEntry]:
        # Verify account exists
        ledger_entries = self.ledger_repo.get_by_account_id(account_id)
        if not ledger_entries:
            return []
        
        return ledger_entries
    
    def get_ledger_entries_by_transaction(self, transaction_id: str) -> List[LedgerEntry]:
        # Verify transaction exists
        transaction = self.get_transaction(transaction_id)
        
        ledger_entries = self.ledger_repo.get_by_transaction_id(transaction_id)
        if not ledger_entries:
            return []
        
        return ledger_entries
    
    def save_ledger_entry(self, ledger_entry: LedgerEntry) -> LedgerEntry:
        # Business validation
        self._validate_ledger_entry(ledger_entry)
        return self.ledger_repo.save(ledger_entry)
    
    def _validate_transaction(self, transaction: Transaction):
        if not transaction.id:
            raise ValueError("Transaction ID is required")
        
        if transaction.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        
        if not transaction.currency:
            raise ValueError("Transaction currency is required")
    
    def _validate_ledger_entry(self, ledger_entry: LedgerEntry):
        if not ledger_entry.account_id:
            raise ValueError("Account ID is required")
        
        if not ledger_entry.transaction_id:
            raise ValueError("Transaction ID is required")
        
        if ledger_entry.amount <= 0:
            raise ValueError("Ledger entry amount must be positive")
        
        if ledger_entry.direction not in ["DEBIT", "CREDIT"]:
            raise ValueError("Ledger direction must be DEBIT or CREDIT")