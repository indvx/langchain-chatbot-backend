from sqlalchemy import Column, Integer, String
from datetime import datetime
from db import Base
from sqlalchemy.orm import relationship
from sql.models.employee_addresses import employeeAddresses


# SQLAlchemy ORM model for employee accounts.
class Employee(Base):
    """
    Main user entity representing staff members.
    
    Fields:
        password: stores the salted bcrypt hash (never plaintext).
        employee_type: role classification (e.g. 'admin', 'employee') used for access levels.
        addresses: one-to-many relationship back-populated from employeeAddresses.
    """
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=True, default=False)
    employee_type = Column(String(255), nullable=True, default="employee")
    created_at = Column(String(255), default=datetime.now(), nullable=False)
    updated_at = Column(String(255), nullable=True, onupdate=datetime.now())
    # Note: relationship is active via backref='addresses' on employeeAddresses

