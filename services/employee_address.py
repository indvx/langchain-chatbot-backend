import db
from sql.cruds import employee_addresses as employee_address_crud


class EmployeeAddressService:
    def __init__(self):
        self.__db = db.get_db()

    def create_employee_address(self, employee_id, data):
        """Add an address for an employee, resetting existing default if new one is default."""
        try:
            if data.is_default is True:
                employee_address_crud.get_or_update_default_address(
                    self.__db, employee_id, True
                )

            employee_address_crud.create_employee_address(self.__db, employee_id, data)
            return "Address Created Successfully"

        except Exception as e:
            raise ProcessLookupError(str(e))

    def delete_employee_address(self, address_id):
        """Delete an address by ID (cannot delete a default address)."""
        try:
            address = employee_address_crud.get_employee_address_by_id(
                self.__db, address_id
            )

            if not address:
                raise ValueError("Address Not Found")

            if address.is_default:
                raise ValueError("Default Address cannot be deleted")

            employee_address_crud.delete_employee_address(self.__db, address_id)
            return "Address Deleted Successfully"

        except Exception as e:
            raise ProcessLookupError(str(e))

    def read_employee_addresses(self, employee_id: int):
        """Return all addresses for an employee."""
        try:
            address = employee_address_crud.get_employee_addresses(
                self.__db, employee_id
            )
            return {"address": address}

        except Exception as e:
            raise ProcessLookupError(str(e))


