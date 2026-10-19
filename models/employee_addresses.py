from pydantic import BaseModel
from typing import Optional


class EmployeeAddress(BaseModel):
    """
    Schema for employee postal/residential addresses.
    Linked to employees.id via employee_id foreign key.
    is_default flags the primary mailing address for payroll/contact.
    """
    id: Optional[int] = None
    employee_id: int
    address: str
    city: str
    state: str
    zip_code: str
    is_default: bool = False


