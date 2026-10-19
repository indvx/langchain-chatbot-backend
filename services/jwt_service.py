import time
import jwt
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings


# FastAPI route security dependency.
# Intercepts protected endpoints, validates the Bearer token, and handles Swagger UI auth.
class JWTBearer(HTTPBearer):
    """
    FastAPI security dependency for protecting endpoints with JWT Bearer tokens.
    
    Subclassing HTTPBearer gives us two key benefits:
    1. Enables the interactive "Authorize" lock button in Swagger UI (/docs).
    2. Automatically parses the 'Authorization: Bearer <token>' header from incoming requests.
    
    Returns 403 Forbidden if the token is missing, malformed, or expired.
    """

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)  # type: ignore

        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=403, detail="Invalid or missing authentication"
            )

        # Validate signature and expiration timestamp
        self.decode_jwt(credentials.credentials)
        return credentials

    def decode_jwt(self, token: str):
        """
        Decodes and verifies a JWT token.
        Raises HTTP 403 immediately if expired or signed with an invalid secret.
        """
        try:
            decoded = jwt.decode(
                token,
                str(settings.jwt_secret_key).strip(),
                algorithms=[str(settings.jwt_algorithm).strip()],
            )

            # Defensive expiry check against system epoch
            if decoded.get("exp", 0) < time.time():
                raise HTTPException(status_code=403, detail="Token expired")

            return decoded

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=403, detail="Invalid token")

