class DomainError(Exception):
    """Base class for domain errors."""
    pass


class InsufficientFundsError(DomainError):
    pass


class AccountFrozenError(DomainError):
    pass


class AccountClosedError(DomainError):
    pass


class RiskRejectedError(DomainError):
    pass


class InvalidTransactionAmountError(DomainError):
    pass

class AccountNotFound(DomainError):
    pass

class CustomerNotFound(DomainError):
    pass

class TransactionNotFound(DomainError):
    pass

