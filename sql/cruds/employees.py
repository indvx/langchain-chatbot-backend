from sql.models.employees import Employee
from sqlalchemy.orm import Session
import bcrypt
from sqlalchemy import asc, desc, or_



def get_employee_by_id(db: Session, employee_id: int) -> Employee:
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_email(db: Session, email: str) -> Employee:
    return db.query(Employee).filter(Employee.email == email).first()


def create_employee(db: Session, employee_data) -> Employee:
    employee = Employee()
    employee.name = employee_data.name
    employee.email = employee_data.email
    employee.password = _encoded_password(employee_data.password)  # type: ignore

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def _encoded_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def _check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def read_employees(
    db: Session,
    filter: str = '',
    order_by: str = 'id',
    order_direction: str = 'desc',
    limit: int = 10,
    page: int = 1
):
    query = db.query(Employee)

    if filter:
        filter_data = f"%{filter.strip()}%"
        query = query.filter(
            or_(
                Employee.id.like(filter_data),
                Employee.name.like(filter_data),
                Employee.email.like(filter_data),
            )
        )

    if order_by:
        direction = desc if order_direction == 'desc' else asc
        query = query.order_by(direction(getattr(Employee, order_by)))

    total_items = query.count()

    if limit > 0:
        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)

    employees = query.all()

    return {
        "all_items": total_items,
        "employees": employees
    }


def update_employee(db: Session, employee: Employee, new_employee):
    if hasattr(new_employee, 'name') and new_employee.name:
        employee.name = new_employee.name

    if hasattr(new_employee, 'email') and new_employee.email:
        employee.email = new_employee.email

    if hasattr(new_employee, 'password') and new_employee.password:
        employee.password = _encoded_password(new_employee.password)

    if hasattr(new_employee, 'employee_type') and new_employee.employee_type:
        employee.employee_type = new_employee.employee_type

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

