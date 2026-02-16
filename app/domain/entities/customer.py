from dataclasses import dataclass


@dataclass
class Customer:
    id: str
    name: str
    email: str
    status: str = "ACTIVE"

    def __post_init__(self):
        if not self.name:
            raise ValueError("Customer name cannot be empty")
        if not self.email:
            raise ValueError("Customer email cannot be empty")