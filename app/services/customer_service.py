from typing import List, Optional
import uuid
from app.domain.entities.customer import Customer
from app.domain.entities.account import Account
from app.domain.exceptions import CustomerNotFound
from app.repositories.interfaces import CustomerRepository, AccountRepository

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository, 
                 account_repo: AccountRepository):
        self.customer_repo = customer_repo
        self.account_repo = account_repo
    
    def create_customer(self, name: str, email: str, status: str = "ACTIVE") -> Customer:
        # Business logic for customer creation
        self._validate_customer_data(name, email)
        
        # Check if customer already exists
        existing_customer = self.customer_repo.get_by_email(email)
        if existing_customer:
            raise ValueError(f"Customer with email {email} already exists")
        
        # Create customer
        customer = Customer(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            status=status
        )
        
        return self.customer_repo.save(customer)
    
    def get_customer(self, customer_id: str) -> Customer:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFound(f"Customer {customer_id} not found")
        return customer
    
    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        # Verify customer exists
        self.get_customer(customer_id)  # Will raise if not found
        
        return self.account_repo.get_by_customer_id(customer_id)
    
    def update_customer_status(self, customer_id: str, new_status: str) -> Customer:
        customer = self.get_customer(customer_id)
        
        # Business rules for status changes
        if new_status not in ["ACTIVE", "INACTIVE", "SUSPENDED"]:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Check if customer has active accounts before deactivating
        if new_status == "INACTIVE":
            active_accounts = self.account_repo.get_by_customer_id(customer_id)
            if any(account.status == "ACTIVE" for account in active_accounts):
                raise ValueError("Cannot deactivate customer with active accounts")
        
        customer.status = new_status
        return self.customer_repo.save(customer)
    
    def _validate_customer_data(self, name: str, email: str):
        if not name or len(name.strip()) < 2:
            raise ValueError("Customer name must be at least 2 characters")
        
        if not email or "@" not in email:
            raise ValueError("Valid email address is required")