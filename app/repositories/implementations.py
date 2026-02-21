from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.domain.entities.customer import Customer
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction
from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.enums import AccountStatus, TransactionStatus, Direction
from app.repositories.models import (
    CustomerModel,
    AccountModel,
    TransactionModel,
    LedgerEntryModel,
)



# Customer

class SqlCustomerRepository:
    """Implementación ORM del CustomerRepository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, customer: Customer) -> Customer:
        model = CustomerModel(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            status=customer.status,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        model = self.db.query(CustomerModel).filter(
            CustomerModel.id == customer_id
        ).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_by_email(self, email: str) -> Optional[Customer]:
        model = self.db.query(CustomerModel).filter(
            CustomerModel.email == email
        ).first()
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: CustomerModel) -> Customer:
        """Convierte un modelo ORM a una entidad de dominio."""
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            status=model.status,
        )


# Account


class SqlAccountRepository:
    """Implementación ORM del AccountRepository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, account: Account) -> Account:
        model = AccountModel(
            id=account.id,
            customer_id=account.customer_id,
            currency=account.currency,
            balance=account.balance,
            status=account.status,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, account_id: str) -> Optional[Account]:
        model = self.db.query(AccountModel).filter(
            AccountModel.id == account_id
        ).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_by_customer_id(self, customer_id: str) -> list[Account]:
        models = self.db.query(AccountModel).filter(
            AccountModel.customer_id == customer_id
        ).all()
        return [self._to_domain(m) for m in models]

    def update(self, account: Account) -> Account:
        model = self.db.query(AccountModel).filter(
            AccountModel.id == account.id
        ).first()
        if model:
            model.balance = account.balance
            model.status = account.status
            self.db.commit()
            self.db.refresh(model)
            return self._to_domain(model)
        return account

    def _to_domain(self, model: AccountModel) -> Account:
        return Account(
            id=model.id,
            customer_id=model.customer_id,
            currency=model.currency,
            balance=model.balance,
            status=AccountStatus(model.status),
        )


# Transaction

class SqlTransactionRepository:
    """Implementación ORM del TransactionRepository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            id=transaction.id,
            type=transaction.type,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            created_at=transaction.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        model = self.db.query(TransactionModel).filter(
            TransactionModel.id == transaction_id
        ).first()
        if not model:
            return None
        return self._to_domain(model)

    def get_by_account_id(self, account_id: str) -> list[Transaction]:
        """Busca transacciones de una cuenta a través del ledger."""
        ledger_entries = self.db.query(LedgerEntryModel).filter(
            LedgerEntryModel.account_id == account_id
        ).all()
        transaction_ids = list(
            set(entry.transaction_id for entry in ledger_entries)
        )
        if not transaction_ids:
            return []
        models = self.db.query(TransactionModel).filter(
            TransactionModel.id.in_(transaction_ids)
        ).order_by(TransactionModel.created_at.desc()).all()
        return [self._to_domain(m) for m in models]

    def count_recent_by_account(
        self, account_id: str, minutes: int
    ) -> int:
        """Cuenta transacciones aprobadas en los últimos N minutos."""
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        # Encuentra transaction_ids de esta cuenta via ledger
        ledger_entries = self.db.query(LedgerEntryModel).filter(
            LedgerEntryModel.account_id == account_id
        ).all()
        transaction_ids = list(
            set(entry.transaction_id for entry in ledger_entries)
        )
        if not transaction_ids:
            return 0
        count = self.db.query(TransactionModel).filter(
            TransactionModel.id.in_(transaction_ids),
            TransactionModel.created_at >= cutoff,
            TransactionModel.status == TransactionStatus.APPROVED,
        ).count()
        return count

    def sum_daily_by_account(self, account_id: str) -> float:
        """Suma montos de transacciones aprobadas de hoy."""
        today_start = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Encuentra transaction_ids de esta cuenta via ledger
        ledger_entries = self.db.query(LedgerEntryModel).filter(
            LedgerEntryModel.account_id == account_id
        ).all()
        transaction_ids = list(
            set(entry.transaction_id for entry in ledger_entries)
        )
        if not transaction_ids:
            return 0.0
        transactions = self.db.query(TransactionModel).filter(
            TransactionModel.id.in_(transaction_ids),
            TransactionModel.created_at >= today_start,
            TransactionModel.status == TransactionStatus.APPROVED,
        ).all()
        return sum(t.amount for t in transactions)

    def _to_domain(self, model: TransactionModel) -> Transaction:
        return Transaction(
            id=model.id,
            type=model.type,
            amount=model.amount,
            currency=model.currency,
            status=model.status,
            created_at=model.created_at,
        )



# Ledger

class SqlLedgerRepository:
    """Implementación ORM del LedgerRepository."""

    def __init__(self, db: Session):
        self.db = db

    def save(self, entry: LedgerEntry) -> LedgerEntry:
        model = LedgerEntryModel(
            id=entry.id,
            account_id=entry.account_id,
            transaction_id=entry.transaction_id,
            direction=entry.direction,
            amount=entry.amount,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def get_by_account_id(self, account_id: str) -> list[LedgerEntry]:
        models = self.db.query(LedgerEntryModel).filter(
            LedgerEntryModel.account_id == account_id
        ).all()
        return [self._to_domain(m) for m in models]

    def get_by_transaction_id(
        self, transaction_id: str
    ) -> list[LedgerEntry]:
        models = self.db.query(LedgerEntryModel).filter(
            LedgerEntryModel.transaction_id == transaction_id
        ).all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: LedgerEntryModel) -> LedgerEntry:
        return LedgerEntry(
            id=model.id,
            account_id=model.account_id,
            transaction_id=model.transaction_id,
            direction=Direction(model.direction),
            amount=model.amount,
        )