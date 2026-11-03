from fastapi import APIRouter, status, HTTPException, Depends
from models.employee_addresses import EmployeeAddress
from services.employee_address import EmployeeAddressService
from fastapi.responses import JSONResponse
import typing as t

router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    responses={404: {"description": "Not found"}},
)


@router.post("/{employee_id:int}/address", summary="Create new employee address")
def create_employee_address(
    employee_id: int,
    address: EmployeeAddress,
    service: t.Any = Depends(EmployeeAddressService)
) -> JSONResponse:
    """Add an address for an employee."""
    try:
        response = service.create_employee_address(employee_id, address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": response},
    )


@router.get("/{employee_id:int}/address/list", summary="Get employee address list")
def get_employee_address_list(
    employee_id: int,
    service: t.Any = Depends(EmployeeAddressService)
):
    """List all addresses for an employee."""
    try:
        response = service.read_employee_addresses(employee_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return response


@router.delete("/address/{id:int}", summary="Delete employee address by ID")
def delete_employee_address(
    id: int,
    service: t.Any = Depends(EmployeeAddressService)
):
    """Delete an address by ID."""
    try:
        response = service.delete_employee_address(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(
        content={"message": response},
        status_code=status.HTTP_200_OK,
    )


