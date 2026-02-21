from typing import Protocol, Optional
from app.domain.entities.customer import Customer
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction
from app.domain.entities.ledger_entry import LedgerEntry


class CustomerRepository(Protocol):
    """Contrato para persistencia de Customer."""

    def save(self, customer: Customer) -> Customer:
        """Guarda un customer nuevo o actualiza uno existente."""
        ...

    def get_by_id(self, customer_id: str) -> Optional[Customer]:
        """Busca un customer por su ID. Retorna None si no existe."""
        ...

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Busca un customer por email. Útil para validar duplicados."""
        ...


class AccountRepository(Protocol):
    """Contrato para persistencia de Account."""

    def save(self, account: Account) -> Account:
        """Guarda una cuenta nueva o actualiza una existente."""
        ...

    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Busca una cuenta por su ID. Retorna None si no existe."""
        ...

    def get_by_customer_id(self, customer_id: str) -> list[Account]:
        """Retorna todas las cuentas de un customer."""
        ...

    def update(self, account: Account) -> Account:
        """Actualiza una cuenta existente (ej: balance, status)."""
        ...


class TransactionRepository(Protocol):
    """Contrato para persistencia de Transaction."""

    def save(self, transaction: Transaction) -> Transaction:
        """Guarda una transacción."""
        ...

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Busca una transacción por su ID."""
        ...

    def get_by_account_id(self, account_id: str) -> list[Transaction]:
        """
        Retorna las transacciones asociadas a una cuenta.
        Se buscan a través del ledger (ledger_entries).
        """
        ...

    def count_recent_by_account(
        self, account_id: str, minutes: int
    ) -> int:
        """
        Cuenta transacciones recientes de una cuenta en los últimos N minutos.
        Útil para VelocityRule (regla antifraude).
        """
        ...

    def sum_daily_by_account(self, account_id: str) -> float:
        """
        Suma el monto de transacciones de hoy para una cuenta.
        Útil para DailyLimitRule (regla antifraude).
        """
        ...


class LedgerRepository(Protocol):
    """Contrato para persistencia de LedgerEntry."""

    def save(self, entry: LedgerEntry) -> LedgerEntry:
        """Guarda una entrada de ledger."""
        ...

    def get_by_account_id(self, account_id: str) -> list[LedgerEntry]:
        """Retorna todas las entradas de ledger de una cuenta."""
        ...

    def get_by_transaction_id(
        self, transaction_id: str
    ) -> list[LedgerEntry]:
        """Retorna las entradas de ledger de una transacción."""
        ...