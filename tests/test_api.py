import pytest
from app.application.banking_facade import BankingFacade
from app.application.dtos import CustomerCreate, AccountCreate, AccountDeposit, AccountWithdraw, TransferRequest
from app.domain.entities.customer import Customer
from app.domain.entities.account import Account
from app.domain.entities.transaction import Transaction
from app.domain.exceptions import AccountNotFound
from app.repositories.implementations import SqlCustomerRepository, SqlAccountRepository, SqlTransactionRepository, SqlLedgerRepository

@pytest.fixture
def banking_facade():
    # Create in-memory repositories for testing
    customer_repo = SqlCustomerRepository(None)  # No DB needed for basic tests
    account_repo = SqlAccountRepository(None)
    transaction_repo = SqlTransactionRepository(None)
    ledger_repo = SqlLedgerRepository(None)
    
    return BankingFacade(
        bank_currency="USD",
        customer_repository=customer_repo,
        account_repository=account_repo,
        transaction_repository=transaction_repo,
        ledger_repository=ledger_repo
    )

def test_create_customer_basic(banking_facade):
    # Arrange
    customer_dto = CustomerCreate(name="John Doe", email="john@example.com", status="ACTIVE")
    
    # Act
    result = banking_facade.create_customer(customer_dto)
    
    # Assert
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert result.status == "ACTIVE"
    assert result.id is not None

def test_create_account_basic(banking_facade):
    # Arrange
    account_dto = AccountCreate(
        customer_id="cust123",
        currency="USD",
        balance=100.0,
        status="ACTIVE"
    )
    
    # Act
    result = banking_facade.create_account(account_dto)
    
    # Assert
    assert result.customer_id == "cust123"
    assert result.currency == "USD"
    assert result.balance == 100.0
    assert result.status == "ACTIVE"
    assert result.id is not None

def test_deposit_amount_validation(banking_facade):
    # This will test the validation logic without needing a real account
    account = Account(id="test", customer_id="cust1", currency="USD", balance=100.0)
    
    # Test valid deposit
    account.deposit(50.0)
    assert account.balance == 150.0
    
    # Test invalid deposit (should raise error)
    with pytest.raises(ValueError):
        account.deposit(-10.0)

def test_withdraw_insufficient_funds(banking_facade):
    # Test domain logic directly
    account = Account(id="test", customer_id="cust1", currency="USD", balance=100.0)
    
    # Test insufficient funds
    with pytest.raises(Exception):  # Should raise InsufficientFundsError
        account.withdraw(200.0)
    
    # Test valid withdrawal
    account.withdraw(50.0)
    assert account.balance == 50.0