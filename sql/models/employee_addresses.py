from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base


# SQLAlchemy ORM model for employee physical addresses.
class employeeAddresses(Base):
    """
    Stores physical/mailing addresses linked to employees.
    An employee can have multiple addresses, with 'is_default' designating
    their primary active residence.
    """
    __tablename__ = "employee_addresses"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    address = Column(String(250), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.now)
    # Establishes bi-directional link to Employee, exposed on Employee as employee.addresses
    employee = relationship("Employee", backref="addresses")

