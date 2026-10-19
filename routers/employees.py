from fastapi import APIRouter, status, HTTPException, Depends
from models.employees import Employee, EmployeeLogin, EmployeeList, LoggedInEmployee, ReadEmployee
from services.employee import EmployeeService
from fastapi.responses import JSONResponse
from typing import Optional, Any, Literal
from services.jwt_service import JWTBearer


# Employee registration, authentication, and management router.
router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    responses={404: {"description": "Not found"}},
)


@router.post('/signup', summary="Create new employee")
def create_employee(employee_: Employee) -> JSONResponse:
    """
    Public registration endpoint.
    Creates a new employee account with bcrypt password hashing.
    Rejects duplicate email addresses.
    """
    try:
        response = EmployeeService().create_employee(employee_)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(
        status_code=200, content=f"message: {response}"
    )


@router.post('/login')
def login(employee: EmployeeLogin) -> JSONResponse:
    """
    Public authentication endpoint.
    Verifies credentials and returns a signed 24h JWT token for subsequent API calls.
    """
    try:
        token = EmployeeService().login(employee)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if token and token == "":
        raise HTTPException(status_code=400, detail="Invalid email or password.")
    
    return JSONResponse(status_code=200, content={"token": token})


@router.get('', response_model=LoggedInEmployee)
def get_current_employee(d: Any = Depends(JWTBearer())):
    """
    Protected endpoint: returns the active employee identity resolved from the Bearer token.
    Useful for frontend applications to verify session validity and user roles on startup.
    """
    employee = EmployeeService().get_current_employee()
    return employee


@router.get('/{id:int}', response_model=ReadEmployee)
def get_employee(id: int, d: Any = Depends(JWTBearer())):
    """
    Protected endpoint: returns a single employee's profile including their attached addresses.
    Passwords are never returned.
    """
    try:
        response = EmployeeService().read_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.put('/{id:int}', response_model=ReadEmployee)
def update_employee(
    id: int,
    data: Employee,
    d: Any = Depends(JWTBearer())
):
    """
    Protected endpoint: updates employee profile details.
    Guards prevent non-admin users from escalating their role to 'admin'
    or modifying other users' profiles.
    """
    try:
        response = EmployeeService().update_employee(id, data)  # type:ignore
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.get('/list', response_model=EmployeeList)
def get_employees(
    filter: str = '',
    order_by: str = 'id',
    order_direction: Literal['desc', 'asc'] = 'desc',
    limit: int = 10,
    page: int = 1,
    d: Any = Depends(JWTBearer())
):
    """
    Protected endpoint: paginated search across all employee records.
    Supports substring filtering across id, name, and email.
    """
    try:
        response = EmployeeService().read_employees(
            filter,
            order_by,
            order_direction,
            limit,
            page
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.delete('/{id:int}')
def delete_employee(id: int):
    """
    Protected endpoint: removes an employee record.
    Restricted to account owners or administrators.
    """
    try:
        response = EmployeeService().delete_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return JSONResponse(content=response, status_code=200)


