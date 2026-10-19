import db
from sql.cruds import employee_addresses as employee_address_crud
from decouple import config
from dotenv import load_dotenv
from middleware.auth_middleware import get_current_employee

load_dotenv()



# Business logic service for employee addresses.
# Coordinates creation, deletion guards (e.g. protecting default addresses), and ownership permissions.
class EmployeeAddressService:
    def __init__(self):
        self.__db = db.get_db()

    def create_employee_address(self, employee_id, data):
        """
        Attaches a new address to an employee.
        If marked as default, unsets the default status on any existing address
        to enforce the single-default-address constraint.
        """
        try:
            logged_in_employee = get_current_employee()
            if not logged_in_employee:
                raise PermissionError("Access Denied")

            # Demote current default address if the new one should become default
            if data.is_default is True:
                employee_address_crud.get_or_update_default_address(
                    self.__db, employee_id, True
                )

            employee_address_crud.create_employee_address(self.__db, employee_id, data)
            return "Address Created Successfully"

        except Exception as e:
            raise ProcessLookupError(str(e))

    def delete_employee_address(self, address_id):
        """
        Removes an address record with safety checks:
        - Must be authenticated as admin or the employee owning the address.
        - Prevents deleting the default address (forces the user to pick another default first).
        """
        try:
            logged_in_employee = get_current_employee()
            if not logged_in_employee:
                raise PermissionError("Access Denied")

            address = employee_address_crud.get_employee_address_by_id(
                self.__db, address_id
            )

            if not address:
                raise ValueError("Address Not Found")

            # Business rule: an employee cannot be left without a primary address
            if address.is_default:  # type: ignore
                raise ValueError("Default Address cannot be deleted")

            # Ownership check: non-admins cannot delete other employees' addresses
            if (
                logged_in_employee.employee_type != 'admin'
                and logged_in_employee.id != address.employee_id
            ):
                raise PermissionError("Access Denied")

            employee_address_crud.delete_employee_address(self.__db, address_id)
            return "Address Deleted Successfully"

        except Exception as e:
            raise ProcessLookupError(str(e))

    def read_employee_addresses(self, employee_id: int):
        """
        Retrieves all address records associated with an employee.
        Restricted to the employee themselves or an administrator.
        """
        try:
            logged_in_employee = get_current_employee()
            if not logged_in_employee:
                raise PermissionError("Access Denied")

            if (
                logged_in_employee.employee_type != "admin"
                and logged_in_employee.id != employee_id
            ):
                raise PermissionError("Access Denied.")

            address = employee_address_crud.get_employee_addresses(
                self.__db, employee_id
            )
            return {"address": address}

        except Exception as e:
            raise ProcessLookupError(str(e))


