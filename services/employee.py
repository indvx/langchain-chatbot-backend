import db
from sql.cruds import employees as employee_crud


class EmployeeService:
    def __init__(self):
        self.__db = db.get_db()

    def create_employee(self, employee_data):
        """Registers a new employee."""
        try:
            employee = employee_crud.get_employee_by_email(
                self.__db, employee_data.email
            )
            if employee:
                raise ValueError("Please use a different email address.")
            employee_crud.create_employee(self.__db, employee_data)
            return "Employee has been created successfully."
        except Exception as e:
            raise LookupError(str(e))

    def read_employee(self, id: int):
        """Fetches detailed profile for an employee by primary key ID."""
        try:
            employee = employee_crud.get_employee_by_id(self.__db, id)
            if not employee:
                raise ValueError("Employee detail not found.")
            return employee
        except Exception as e:
            raise ProcessLookupError(str(e))

    def read_employees(
        self,
        filter: str = "",
        order_by: str = "id",
        order_direction: str = "desc",
        limit: int = 10,
        page: int = 1,
    ):
        """Returns a paginated list of employees with metadata envelope."""
        try:
            if limit < 1:
                limit = 10
            if page < 1:
                page = 1

            data = employee_crud.read_employees(
                self.__db, filter, order_by, order_direction, limit, page
            )

            all_items = data["all_items"]
            employees = data["employees"]
            meta = {
                "current_item": len(employees),
                "limit": limit,
                "page": page,
                "total_items": all_items,
            }

            return {"meta": meta, "employees": employees}
        except Exception as e:
            raise ProcessLookupError(str(e))

    def delete_employee(self, id: int):
        """Removes an employee record."""
        try:
            employee = employee_crud.get_employee_by_id(self.__db, id)
            if employee:
                self.__db.delete(employee)
                self.__db.commit()
                return "Employee deleted successfully."

            raise ValueError("Employee detail not found.")
        except Exception as e:
            raise ProcessLookupError(str(e))

    def update_employee(self, id: int, data):
        """Updates an employee profile."""
        try:
            employee = employee_crud.get_employee_by_id(self.__db, id)
            if not employee:
                raise ValueError("Please provide valid details.")

            if hasattr(data, "email") and data.email:
                employee_by_email = employee_crud.get_employee_by_email(
                    self.__db, data.email
                )
                if employee_by_email and employee.id != employee_by_email.id:
                    raise ValueError("Provided email already exists.")

            employee = employee_crud.update_employee(self.__db, employee, data)
            return employee
        except Exception as e:
            raise ProcessLookupError(str(e))

