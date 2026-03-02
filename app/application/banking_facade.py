import uuid
from app.domain.entities.account import Account
from app.domain.entities.customer import Customer
from app.domain.entities.transaction import Transaction
from app.domain.enums import AccountStatus, Direction, TransactionType, TransactionStatus
from app.domain.exceptions import AccountNotFound, CustomerNotFound
from app.domain.factories.ledger_entry_factory import LedgerEntryFactory
from app.domain.factories.transaction_factory import TransactionFactory
from app.domain.strategies.fee_strategy import FeeStrategy
from app.domain.strategies.risk_strategy import RiskStrategy
from app.repositories.implementations import (
    SqlAccountRepository,
    SqlCustomerRepository,
    SqlLedgerRepository,
    SqlTransactionRepository,
)


class BankingFacade:
    def __init__(
        self,
        customer_repository: SqlCustomerRepository,
        account_repository: SqlAccountRepository,
        transaction_repository: SqlTransactionRepository,
        ledger_repository: SqlLedgerRepository,
        fee_strategy: FeeStrategy,
        risk_rules: list[RiskStrategy],
    ):
        self.customer_repo = customer_repository
        self.account_repo = account_repository
        self.transaction_repo = transaction_repository
        self.ledger_repo = ledger_repository
        self.fee_strategy = fee_strategy
        self.risk_rules = risk_rules

    def create_customer(self, name: str, email: str) -> Customer:
        customer = Customer(id=str(uuid.uuid4()), name=name, email=email)
        self.customer_repo.save(customer)
        return customer

    def create_account(self, customer_id: str, currency: str = "USD") -> Account:
        customer = self.customer_repo.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFound(f"Customer {customer_id} not found")
        account = Account(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            currency=currency,
        )
        self.account_repo.save(account)
        return account

    def get_account(self, account_id: str) -> Account:
        account = self.account_repo.get_by_id(account_id)
        if account is None:
            raise AccountNotFound(f"Account {account_id} not found")
        return account

    def list_transactions(self, account_id: str) -> list[Transaction]:
        return self.transaction_repo.get_by_account_id(account_id)

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
        account = self.get_account(account_id)
        self._run_risk_checks(amount, account_id)

        fee = self.fee_strategy.calculate(amount)
        net_amount = amount - fee

        transaction = TransactionFactory.create(
            TransactionType.DEPOSIT, amount, account.currency
        )

        account.deposit(net_amount)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(account)

        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=account.id,
            transaction_id=transaction.id,
            direction=Direction.CREDIT,
            amount=net_amount,
        ))

        return transaction

    def withdraw(self, account_id: str, amount: float) -> Transaction:
        account = self.get_account(account_id)
        self._run_risk_checks(amount, account_id)

        fee = self.fee_strategy.calculate(amount)
        total_debit = amount + fee

        transaction = TransactionFactory.create(
            TransactionType.WITHDRAW, amount, account.currency
        )

        account.withdraw(total_debit)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(account)

        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=account.id,
            transaction_id=transaction.id,
            direction=Direction.DEBIT,
            amount=total_debit,
        ))

        return transaction

    def transfer(self, from_account_id: str, to_account_id: str, amount: float) -> Transaction:
        from_account = self.get_account(from_account_id)
        to_account = self.get_account(to_account_id)
        self._run_risk_checks(amount, from_account_id)

        fee = self.fee_strategy.calculate(amount)
        total_debit = amount + fee

        transaction = TransactionFactory.create(
            TransactionType.TRANSFER, amount, from_account.currency
        )

        from_account.withdraw(total_debit)
        to_account.deposit(amount)
        transaction.status = TransactionStatus.APPROVED

        self.transaction_repo.save(transaction)
        self.account_repo.update(from_account)
        self.account_repo.update(to_account)

        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=from_account.id,
            transaction_id=transaction.id,
            direction=Direction.DEBIT,
            amount=total_debit,
        ))
        self.ledger_repo.save(LedgerEntryFactory.create(
            account_id=to_account.id,
            transaction_id=transaction.id,
            direction=Direction.CREDIT,
            amount=amount,
        ))

        return transaction