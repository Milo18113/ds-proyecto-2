from dataclasses import dataclass
from app.domain.enums import Direction


@dataclass
class LedgerEntry:
    id: str
    account_id: str
    transaction_id: str
    direction: Direction
    amount: float