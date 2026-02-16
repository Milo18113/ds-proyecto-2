import uuid
from app.domain.entities.transaction import Transaction
from app.domain.enums import TransactionType


class TransactionFactory:
    @staticmethod
    def create(transaction_type: TransactionType, amount: float, currency: str):
        return Transaction(
            id=str(uuid.uuid4()),
            type=transaction_type,
            amount=amount,
            currency=currency,
        )