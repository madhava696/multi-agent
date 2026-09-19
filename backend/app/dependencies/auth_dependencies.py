from fastapi import HTTPException,Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth_models import UserResponse
from app.dependencies.services import auth_service,token_service

security = HTTPBearer()

def get_current_user(authorization: HTTPAuthorizationCredentials=Security(security)) -> UserResponse:
    if authorization.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid bearer token.")


    token = authorization.credentials
    try:
        payload = token_service.decode_access_token(token)

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token subject is missing.")
        user = auth_service.get_user(email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc
