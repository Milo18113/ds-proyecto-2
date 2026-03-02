import uuid
from app.domain.entities.ledger_entry import LedgerEntry
from app.domain.enums import Direction


class LedgerEntryFactory:
    @staticmethod
    def create(account_id: str, transaction_id: str, direction: Direction, amount: float) -> LedgerEntry:
        return LedgerEntry(
            id=str(uuid.uuid4()),
            account_id=account_id,
            transaction_id=transaction_id,
            direction=direction,
            amount=amount
        )