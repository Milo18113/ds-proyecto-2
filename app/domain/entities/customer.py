from dataclasses import dataclass
import email
import uuid

from numpy import isin

from app.application.dtos import CustomerCreate, CustomerResponse, CustomerUpdate


@dataclass
class Customer:
    id: str  # = str(uuid.uuid4())
    name: str
    email: str
    status: str = "ACTIVE"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Customer name cannot be empty")
        if not self.email:
            raise ValueError("Customer email cannot be empty")

    @staticmethod
    def create_from_dto(dto: CustomerCreate | CustomerResponse):
        return Customer(
            id = uuid.uuid4() if isinstance(dto, CustomerCreate) else dto.id,
            name=dto.name,
            email=dto.email,
            status=dto.status
        )

    def update_from_dto(self, dto: CustomerUpdate):
        if dto.name is not None:  
            self.name = dto.name
        if dto.email is not None: 
            self.email = dto.email