import pytest
from app.domain.entities.account import Account
from app.domain.enums import AccountStatus
from app.domain.exceptions import (
    InsufficientFundsError,
    AccountFrozenError,
)


def test_withdraw_insufficient_funds():
    account = Account(
        id="1",
        customer_id="cust1",
        currency="USD",
        balance=100.0,
        status=AccountStatus.ACTIVE,
    )

    with pytest.raises(InsufficientFundsError):
        account.withdraw(200.0)


def test_account_frozen_cannot_withdraw():
    account = Account(
        id="1",
        customer_id="cust1",
        currency="USD",
        balance=100.0,
        status=AccountStatus.FROZEN,
    )

    with pytest.raises(AccountFrozenError):
        account.withdraw(50.0)