from typing import Protocol
from app.domain.exceptions import RiskRejectedError


class RiskStrategy(Protocol):
    def validate(self, amount: float, context: dict) -> None:
        ...


class MaxAmountRule:
    def __init__(self, max_amount: float):
        self.max_amount = max_amount

    def validate(self, amount: float, context: dict) -> None:
        if amount > self.max_amount:
            raise RiskRejectedError("Amount exceeds maximum allowed")


class VelocityRule:
    def __init__(self, max_transactions: int):
        self.max_transactions = max_transactions

    def validate(self, amount: float, context: dict) -> None:
        tx_count = context.get("recent_transactions", 0)
        if tx_count > self.max_transactions:
            raise RiskRejectedError("Velocity limit exceeded")


class DailyLimitRule:
    def __init__(self, daily_limit: float):
        self.daily_limit = daily_limit

    def validate(self, amount: float, context: dict) -> None:
        total_today = context.get("daily_total", 0)
        if total_today + amount > self.daily_limit:
            raise RiskRejectedError("Daily limit exceeded")