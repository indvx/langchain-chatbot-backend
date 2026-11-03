from fastapi import APIRouter, HTTPException, Depends
from models.employees import Employee, EmployeeList, ReadEmployee
from services.employee import EmployeeService
from fastapi.responses import JSONResponse
import typing as t

router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    responses={404: {"description": "Not found"}},
)


@router.post('', summary="Create new employee")
@router.post('/signup', summary="Create new employee")
def create_employee(
    employee_: Employee,
    service: t.Any = Depends(EmployeeService)
    ) -> JSONResponse:
    """Create a new employee."""
    try:
        response = service.create_employee(employee_)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=200, content=f"message: {response}"
    )


@router.get('/list', response_model=EmployeeList)
def get_employees(
    filter: str = '',
    order_by: str = 'id',
    order_direction: t.Literal['desc', 'asc'] = 'desc',
    limit: int = 10,
    page: int = 1,
    service: t.Any = Depends(EmployeeService)
):
    """List employees with pagination and optional search filter."""
    try:
        response = service.read_employees(
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
def get_employee(id: int, service: t.Any = Depends(EmployeeService)):
    """Get an employee by ID with their addresses."""
    try:
        response = service.read_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.put('/{id:int}', response_model=ReadEmployee)
def update_employee(
    id: int,
    data: Employee,
    service: t.Any = Depends(EmployeeService)
):
    """Update employee details by ID."""
    try:
        response = service.update_employee(id, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return response


@router.delete('/{id:int}')
def delete_employee(id: int, service: t.Any = Depends(EmployeeService)):
    """Delete an employee by ID."""
    try:
        response = service.delete_employee(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content=response, status_code=200)


