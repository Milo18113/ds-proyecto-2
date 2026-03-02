from dataclasses import dataclass
import uuid
from app.domain.enums import AccountStatus
from app.domain.exceptions import (
    InsufficientFundsError,
    AccountFrozenError,
    AccountClosedError,
)


@dataclass
class Account:
    id: str
    customer_id: str
    currency: str
    balance: float = 0.0
    status: AccountStatus = AccountStatus.ACTIVE

    def deposit(self, amount: float):
        self._validate_active()
        self._validate_amount(amount)
        self.balance += amount

    def withdraw(self, amount: float):
        self._validate_active()
        self._validate_amount(amount)
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient balance")
        self.balance -= amount

    def transfer(self, amount: float, to_account: 'Account'):
        self._validate_active()
        self._validate_amount(amount)
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient balance")
        self.balance -= amount
        to_account.deposit(amount)

    def freeze(self):
        self.status = AccountStatus.FROZEN

    def close(self):
        self.status = AccountStatus.CLOSED

    def _validate_active(self):
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError("Account is frozen")
        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("Account is closed")

    def _validate_amount(self, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")