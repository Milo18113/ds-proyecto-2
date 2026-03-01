from dataclasses import dataclass
import uuid

from sqlalchemy import Transaction

from app.application.dtos import (
    AccountCreate, 
    AccountResponse, 
    AccountUpdate,
    AccountDeposit,
    AccountWithdraw
)
from app.domain.enums import AccountStatus
from app.domain.exceptions import (
    InsufficientFundsError,
    AccountFrozenError,
    AccountClosedError,
)


@dataclass
class Account:
    id: str = str(uuid.uuid4())
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

    @staticmethod
    def create_from_dto(dto: AccountCreate | AccountResponse):
        return Account(
            id=uuid.uuid4() if isinstance(dto, AccountCreate) else dto.id,
            customer_id=dto.customer_id,
            currency=dto.currency,
            balance=dto.balance,
            status=dto.status
        )

    def update_from_dto(self, dto: AccountUpdate):
        if dto.status is not None:
            self.status = dto.status

    def deposit_from_dto(self, dto: AccountDeposit):
        self.deposit(dto.amount)

    def withdraw_from_dto(self, dto: AccountWithdraw):
        self.withdraw(dto.amount)