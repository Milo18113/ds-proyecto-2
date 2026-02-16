from typing import Protocol


class FeeStrategy(Protocol):
    def calculate(self, amount: float) -> float:
        ...


class NoFeeStrategy:
    def calculate(self, amount: float) -> float:
        return 0.0


class FlatFeeStrategy:
    def __init__(self, fee: float):
        self.fee = fee

    def calculate(self, amount: float) -> float:
        return self.fee


class PercentFeeStrategy:
    def __init__(self, percent: float):
        self.percent = percent  

    def calculate(self, amount: float) -> float:
        return amount * self.percent


class TieredFeeStrategy:
    def __init__(self, threshold: float, low_fee: float, high_fee: float):
        self.threshold = threshold
        self.low_fee = low_fee
        self.high_fee = high_fee

    def calculate(self, amount: float) -> float:
        if amount <= self.threshold:
            return self.low_fee
        return self.high_fee