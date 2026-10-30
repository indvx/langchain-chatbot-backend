from fastapi import APIRouter, HTTPException
from models.employees import Employee, EmployeeList, ReadEmployee
from services.employee import EmployeeService
from fastapi.responses import JSONResponse
from typing import Literal

# Employee management router
router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    responses={404: {"description": "Not found"}},
)


@router.post('', summary="Create new employee")
@router.post('/signup', summary="Create new employee")
def create_employee(employee_: Employee) -> JSONResponse:
    """Creates a new employee account."""
    try:
        response = EmployeeService().create_employee(employee_)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=200, content=f"message: {response}"
    )


@router.get('/list', response_model=EmployeeList)
def get_employees(
    filter: str = '',
    order_by: str = 'id',
    order_direction: Literal['desc', 'asc'] = 'desc',
    limit: int = 10,
    page: int = 1,
):
    """Paginated search across employee records."""
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


@router.get('/{id:int}', response_model=ReadEmployee)
def get_employee(id: int):
    """Returns a single employee's profile including attached addresses."""
    try:
        response = EmployeeService().read_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.put('/{id:int}', response_model=ReadEmployee)
def update_employee(
    id: int,
    data: Employee,
):
    """Updates employee profile details."""
    try:
        response = EmployeeService().update_employee(id, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.delete('/{id:int}')
def delete_employee(id: int):
    """Removes an employee record."""
    try:
        response = EmployeeService().delete_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response, status_code=200)


