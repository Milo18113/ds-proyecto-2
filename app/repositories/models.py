from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum as SqlEnum,
)
from app.repositories.database import Base
from app.domain.enums import (
    AccountStatus,
    TransactionStatus,
    TransactionType,
    Direction,
)

#Tabla: customers
class CustomerModel(Base):

    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default="ACTIVE")

#Tabla: accounts
class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    currency = Column(String, nullable=False, default="USD")
    balance = Column(Float, nullable=False, default=0.0)
    status = Column(
        SqlEnum(AccountStatus),
        nullable=False,
        default=AccountStatus.ACTIVE,
    )

#Tabla: transactions
class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    type = Column(SqlEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    status = Column(
        SqlEnum(TransactionStatus),
        nullable=False,
        default=TransactionStatus.PENDING,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

#Tabla: ledger_entries
class LedgerEntryModel(Base):
    __tablename__ = "ledger_entries"

    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    transaction_id = Column(
        String, ForeignKey("transactions.id"), nullable=False
    )
    direction = Column(SqlEnum(Direction), nullable=False)
    amount = Column(Float, nullable=False)