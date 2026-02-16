from enum import Enum


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class TransactionType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


class Direction(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"