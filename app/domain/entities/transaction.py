from dataclasses import dataclass, field
from datetime import datetime
from app.domain.enums import TransactionStatus, TransactionType
from app.domain.exceptions import InvalidTransactionAmountError


@dataclass
class Transaction:
    id: str
    type: TransactionType
    amount: float
    currency: str
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.amount <= 0:
            raise InvalidTransactionAmountError(
                "Transaction amount must be greater than zero"
            )