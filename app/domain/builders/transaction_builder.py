import uuid
from datetime import datetime
from app.domain.entities.transaction import Transaction
from app.domain.enums import TransactionStatus, TransactionType
from app.domain.exceptions import InvalidTransactionAmountError


class TransactionBuilder:
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._type = None
        self._amount = None
        self._currency = "USD"
        self._status = TransactionStatus.PENDING
        self._created_at = datetime.utcnow()

    def with_type(self, tx_type: TransactionType):
        self._type = tx_type
        return self

    def with_amount(self, amount: float):
        self._amount = amount
        return self

    def with_currency(self, currency: str):
        self._currency = currency
        return self

    def approved(self):
        self._status = TransactionStatus.APPROVED
        return self

    def rejected(self):
        self._status = TransactionStatus.REJECTED
        return self

    def build(self):
        if self._type is None or self._amount is None:
            raise InvalidTransactionAmountError("El tipo o cantidad de la transacción no puede ser None")
        return Transaction(
            id=self._id,
            type=self._type,
            amount=self._amount,
            currency=self._currency,
            status=self._status,
            created_at=self._created_at,
        )