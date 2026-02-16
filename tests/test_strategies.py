import pytest
from app.domain.strategies.fee_strategy import PercentFeeStrategy
from app.domain.strategies.risk_strategy import MaxAmountRule
from app.domain.exceptions import RiskRejectedError


def test_percent_fee_calculation():
    strategy = PercentFeeStrategy(0.10)  # 10%
    fee = strategy.calculate(100.0)

    assert fee == 10.0


def test_max_amount_rule_rejects():
    rule = MaxAmountRule(max_amount=100.0)

    with pytest.raises(RiskRejectedError):
        rule.validate(amount=150.0, context={})