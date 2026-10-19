import db
from sql.cruds import employees as employee_crud
import jwt
from datetime import datetime, timedelta
from core.config import settings
from middleware.auth_middleware import get_current_employee


# Employee account and authentication business logic service.
# Manages registrations, login sessions, role validations, and profile modifications.
class EmployeeService:
    def __init__(self):
        self.__db = db.get_db()

    def create_employee(self, employee_data):
        """
        Registers a new employee.
        Verifies that the requested email address is not already registered before saving.
        """
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

    def login(self, employee_data):
        """
        Authenticates an employee using email and password.
        On success, issues a signed JWT token with a 24-hour expiration window.
        """
        try:
            employee_name = employee_data.email
            password = employee_data.password
            employee = employee_crud.get_employee_by_email(self.__db, employee_name)
            token = None

            if employee:
                # Validate against bcrypt salt and hash
                if employee_crud._check_password(password, employee.password):
                    token = jwt.encode(
                        {
                            "exp": datetime.utcnow() + timedelta(days=1),
                            "iat": datetime.utcnow(),
                            "email": employee.email,
                            "id": employee.id,
                        },
                        str(settings.jwt_secret_key),
                        str(settings.jwt_algorithm),
                    )
                else:
                    raise ValueError("Invalid employee username or password")

            if token is None:
                raise ValueError("Invalid employee username or password")

            return token
        except Exception as e:
            raise ProcessLookupError(str(e))

    def get_current_employee(self):
        """Returns the logged-in employee context stored in the current request scope."""
        try:
            employee = get_current_employee()
            return employee
        except Exception as e:
            raise ProcessLookupError(str(e))

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
        """
        Removes an employee record.
        Restricted to admins or the employee deleting their own account.
        """
        try:
            logged_in_employee = get_current_employee()
            if not logged_in_employee:
                raise PermissionError("Access denied")

            employee = employee_crud.get_employee_by_id(self.__db, id)
            if employee and (
                logged_in_employee.id == employee.id
                or logged_in_employee.employee_type == "admin"
            ):
                self.__db.delete(employee)
                self.__db.commit()
                return "Employee deleted successfully."

            raise ValueError("Employee detail not found.")
        except Exception as e:
            raise ProcessLookupError(str(e))

    def update_employee(self, id: int, data):
        """
        Updates an employee profile with safety guardrails:
        - Only admins or the owner can edit the account.
        - Checks for email collisions if updating the email address.
        - Prevents non-admins from elevating their role to 'admin'.
        """
        try:
            logged_in_employee = get_current_employee()
            if not logged_in_employee:
                raise PermissionError("Access denied")

            employee = employee_crud.get_employee_by_id(self.__db, id)
            if not employee:
                raise ValueError("Please provide valid details.")

            # Authorization guard: owner or admin
            if logged_in_employee.employee_type != "admin" and employee.id != id:  # type: ignore
                raise PermissionError("Access denied")

            # Check that new email is not taken by another user
            if hasattr(data, "email") and data.email != "":
                employee_by_email = employee_crud.get_employee_by_email(
                    self.__db, data.email
                )
                if employee_by_email and employee.id != employee_by_email.id:  # type: ignore
                    raise ValueError("Provided email already exists.")

            # Privilege escalation guard: only existing admins can grant admin status
            if hasattr(data, "employee_type") and data.employee_type:
                if (
                    data.employee_type == "admin"
                    and logged_in_employee.employee_type == "admin"
                ):
                    pass
                else:
                    data.employee_type = "employee"

            employee = employee_crud.update_employee(self.__db, employee, data)
            return employee
        except Exception as e:
            raise ProcessLookupError(str(e))

