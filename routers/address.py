from fastapi import APIRouter, status, HTTPException, Depends
from models.employee_addresses import EmployeeAddress
from services.employee_address import EmployeeAddressService
from fastapi.responses import JSONResponse
from typing import Any
from services.jwt_service import JWTBearer
from fastapi.requests import Request


# Employee address management API router.
# Handles postal/residential addresses attached to employees.
# All operations require a valid JWT Bearer token and enforce ownership checks.
router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{employee_id:int}/address", summary="Create new employee address")
def create_employee_address(
    employee_id: int,
    address: EmployeeAddress,
    d: Any = Depends(JWTBearer())
) -> JSONResponse:
    """
    Attaches a new address to an employee.
    If 'is_default' is set to True, any prior default address for this employee
    is automatically demoted to False to maintain exactly one default.
    """
    try:
        response = EmployeeAddressService().create_employee_address(employee_id, address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": response},
    )


@router.get("/{employee_id:int}/address/list", summary="Get employee address list")
def get_employee_address_list(
    employee_id: int,
    d: Any = Depends(JWTBearer())
):
    """
    Retrieves all registered addresses for a specific employee.
    Restricted to the employee themselves or administrators.
    """
    try:
        response = EmployeeAddressService().read_employee_addresses(employee_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.delete("/address/{id:int}", summary="Delete employee address by ID")
def delete_employee_address(
    id: int,
    d: Any = Depends(JWTBearer())
):
    """
    Deletes an address by its ID.
    Rejects deletion if the address is currently marked as default
    (a replacement default address must be designated first).
    """
    try:
        response = EmployeeAddressService().delete_employee_address(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        content={"message": response},
        status_code=status.HTTP_200_OK,
    )


