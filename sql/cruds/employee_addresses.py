from sqlalchemy.orm import Session
from sql.models.employee_addresses import employeeAddresses


# Database CRUD operations for employee addresses.
# Handles address persistence, retrieval, deletion, and default address exclusivity.

def create_employee_address(db: Session, employee_id: int, address):
    """
    Creates and attaches a physical address to an employee.
    If 'is_default' is True, callers should first unset any previously default address.
    """
    employee_address = employeeAddresses()
    employee_address.employee_id = employee_id  # type: ignore
    employee_address.address = address.address
    employee_address.city = address.city
    employee_address.state = address.state
    employee_address.zip_code = address.zip_code
    employee_address.is_default = address.is_default

    db.add(employee_address)
    db.commit()
    db.refresh(employee_address)
    return employee_address


def get_employee_address_by_id(db: Session, address_id: int):
    """Fetch a specific address by its primary key ID."""
    return (
        db.query(employeeAddresses).filter(employeeAddresses.id == address_id).first()
    )


def get_employee_addresses(db: Session, employee_id: int):
    """Retrieve all saved addresses for a given employee."""
    return (
        db.query(employeeAddresses)
        .filter(employeeAddresses.employee_id == employee_id)
        .all()
    )


def delete_employee_address(db: Session, address_id: int):
    """Remove an address record by ID. Returns the deleted record if found, else None."""
    address = (
        db.query(employeeAddresses).filter(employeeAddresses.id == address_id).first()
    )
    if address:
        db.delete(address)
        db.commit()
    return address


def get_or_update_default_address(
    db: Session, employee_id: int, is_default_changed: bool = False
):
    """
    Enforces that an employee can have at most one default address.
    Finds the employee's currently active default address; if 'is_default_changed' is True,
    it demotes that address by setting is_default = False so a new one can take its place.
    """
    address = (
        db.query(employeeAddresses)
        .filter(
            employeeAddresses.employee_id == employee_id,
            employeeAddresses.is_default == True,
        )
        .first()
    )

    if address and is_default_changed:
        address.is_default = False  # type: ignore
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    return address

