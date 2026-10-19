from pydantic import BaseModel, EmailStr
from typing import Optional, List
from models.employee_addresses import EmployeeAddress


# Pydantic schemas for employee account management, authentication, and responses.

class Employee(BaseModel):
    """Payload schema used when registering a new employee or updating details."""
    id: Optional[int] = None
    name: str
    email: EmailStr
    password: str
    employee_type: Optional[str] = ''


class ReadEmployee(BaseModel):
    """
    Public employee profile response.
    Never exposes raw or hashed passwords; includes nested address records.
    """
    id: Optional[int] = None
    name: str
    email: EmailStr
    employee_type: Optional[str] = ''
    addresses: List[EmployeeAddress] = []


class EmployeeLogin(BaseModel):
    """Payload schema for POST /employee/login authentication."""
    email: EmailStr
    password: str


class LoggedInEmployee(BaseModel):
    """
    Decoded employee identity populated by AuthMiddleware from JWT claims
    and attached to the current request lifecycle.
    """
    id: int
    email: str
    name: str
    employee_type: str

    class Config:
        from_attributes = True


class Meta(BaseModel):
    """Standard pagination metadata for employee listings."""
    current_item: Optional[int] = None
    total_items: Optional[int] = None
    limit: Optional[int] = None
    page: Optional[int] = None


class EmployeeList(BaseModel):
    """Paginated collection of employee records returned by GET /employee."""
    meta: Meta
    employees: List[ReadEmployee] = []


