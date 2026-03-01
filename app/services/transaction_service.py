from app.domain.entities.transaction import Transaction
from app.domain.enums import Direction, TransactionType, TransactionStatus
from app.domain.exceptions import AccountNotFound
from app.domain.factories.transaction_factory import TransactionFactory
from app.domain.factories.ledger_entry_factory import LedgerEntryFactory
from app.repositories.interfaces import (
    AccountRepository,
    TransactionRepository,
    LedgerRepository,
)
from app.domain.strategies.fee_strategy import FeeStrategy
from app.domain.strategies.risk_strategy import RiskStrategy


class TransactionService:
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
        ledger_repo: LedgerRepository,
        fee_strategy: FeeStrategy,
        risk_rules: list[RiskStrategy],
    ):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo
        self.ledger_repo = ledger_repo
        self.fee_strategy = fee_strategy
        self.risk_rules = risk_rules

    def _build_risk_context(self, account_id: str) -> dict:
        return {
            "recent_transactions": self.transaction_repo.count_recent_by_account(account_id, minutes=10),
            "daily_total": self.transaction_repo.sum_daily_by_account(account_id),
        }

    def _run_risk_checks(self, amount: float, account_id: str):
        context = self._build_risk_context(account_id)
        for rule in self.risk_rules:
            rule.validate(amount, context)

    def deposit(self, account_id: str, amount: float) -> Transaction:
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise AccountNotFound(f"Account {account_id} not found")

        self._run_risk_checks(amount, account_id)
        fee = self.fee_strategy.calculate(amount)
        net_amount = amount - fee

        transaction = TransactionFactory.create(TransactionType.DEPOSIT, amount, account.currency)
        account.deposit(net_amount)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(account)
        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=account.id, transaction_id=transaction.id,
            direction=Direction.CREDIT, amount=net_amount,
        ))
        return transaction

    def withdraw(self, account_id: str, amount: float) -> Transaction:
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise AccountNotFound(f"Account {account_id} not found")

        self._run_risk_checks(amount, account_id)
        fee = self.fee_strategy.calculate(amount)
        total_debit = amount + fee

        transaction = TransactionFactory.create(TransactionType.WITHDRAW, amount, account.currency)
        account.withdraw(total_debit)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(account)
        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=account.id, transaction_id=transaction.id,
            direction=Direction.DEBIT, amount=total_debit,
        ))
        return transaction

    def transfer(self, from_account_id: str, to_account_id: str, amount: float) -> Transaction:
        from_account = self.account_repo.get_by_id(from_account_id)
        to_account = self.account_repo.get_by_id(to_account_id)
        if from_account is None:
            raise AccountNotFound(f"Account {from_account_id} not found")
        if to_account is None:
            raise AccountNotFound(f"Account {to_account_id} not found")

        self._run_risk_checks(amount, from_account_id)
        fee = self.fee_strategy.calculate(amount)
        total_debit = amount + fee

        transaction = TransactionFactory.create(TransactionType.TRANSFER, amount, from_account.currency)
        from_account.withdraw(total_debit)
        to_account.deposit(amount)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(from_account)
        self.account_repo.update(to_account)
        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=from_account.id, transaction_id=transaction.id,
            direction=Direction.DEBIT, amount=total_debit,
        ))
        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=to_account.id, transaction_id=transaction.id,
            direction=Direction.CREDIT, amount=amount,
        ))
        return transaction