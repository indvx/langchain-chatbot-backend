from alembic import config
import jwt
import time
from dotenv import load_dotenv
from sql.cruds import employees as employee_crud
from models.employees import LoggedInEmployee
from sql.schemas.employees import LoggedInEmployeeSchema
import db
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from core.config import settings


# Global container to hold the employee record for the current request lifecycle.
# Consumed downstream by get_current_employee() across services and endpoints.
global current_employee_var


class AuthMiddleware(BaseHTTPMiddleware):
    """
    HTTP middleware that inspects the 'Authorization: Bearer <token>' header on every request.
    If valid, it extracts the employee ID, loads the employee record from the DB,
    and stores it in module scope for downstream access (e.g. by LangChain service).
    
    If token is invalid or missing, it fails silently so public routes (signup, login,
    webhooks) can still proceed without errors. Protected routes enforce authentication
    explicitly via FastAPI's Depends(JWTBearer()).
    """

    async def dispatch(self, request: Request, call_next):
        global current_employee_var
        # Reset context at the start of each request to prevent state leaking across requests
        current_employee_var = None

        authorization = request.headers.get("Authorization")

        if authorization:
            try:
                # Expecting 'Bearer <jwt_token>' format
                authorization = authorization.split(" ")
                token_type = authorization[0]
                token = authorization[1]

                if token_type.lower() != "bearer":
                    raise HTTPException(
                        status_code=401, detail="Invalid Authorization type"
                    )

                # Validate signature and expiration using application secret key
                payload = jwt.decode(
                    token,
                    str(settings.jwt_secret_key).strip(),
                    algorithms=[str(settings.jwt_algorithm).strip()],
                )

                # Fetch fresh employee details from database
                employee = employee_crud.get_employee_by_id(
                    db.get_db(), payload.get("id", 0)
                )

                employee_dict = LoggedInEmployeeSchema().dump(employee)
                logged_employee = LoggedInEmployee(**employee_dict)  # type: ignore

                current_employee_var = logged_employee

            except Exception:
                # Do not block the request pipeline here; routes that strictly require
                # a valid token use the JWTBearer dependency which returns HTTP 403.
                current_employee_var = None
                pass

        response = await call_next(request)
        return response


def get_current_employee():
    """
    Helper for services/routers (like chatbot RAG) to check if the caller is
    an authenticated employee or an anonymous visitor.
    Returns LoggedInEmployee instance if valid token was present, else None.
    """
    return current_employee_var
