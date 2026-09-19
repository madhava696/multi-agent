import logging 
"""
logging:
->TRACKS APPLICATION FLOW(log when a request starts,when it ends or a certain function is called)
->RECORDS ERRORS(exceptions and stack traces are logged for debugging)

->SUPPORTS MONITORING TOOLS like ELASTICSEARCH,KIBANA,GRAFANA..

"""

from fastapi import APIRouter,HTTPException,status

from app.config.settings import settings
from app.models.auth_models import LoginRequest,RegisterRequest,TokenResponse,UserResponse
from app.dependencies.services import auth_service, token_service

router  = APIRouter(prefix=settings.api_prefix+"/auth",tags=["auth"])
logger  = logging.getLogger(__name__)


@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(request : RegisterRequest)->UserResponse:
    logger.info("Register request received",extra={"user_id":request.email})
    try:
        user = auth_service.register_user(request)
        logger.info("Register request complete",extra={"user_id":request.email})
        return user
    except ValueError as e:
        logger.warning("REgister request failed",extra={"user_id":request.email,"reason":str(e)})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e)) from e


@router.post("/login",response_model=TokenResponse)
def login(request:LoginRequest)->TokenResponse:
    logger.info("Login request received",extra={"user_id":request.email})
    user = auth_service.authenticate_user(request)
    if not user:
        logger.warning("Login request rejected",extra={"user_id":request.email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")

    token = token_service.create_access_token(user.email)
    logger.info("Login request completed",extra={"user_id":request.email})
    return TokenResponse(access_token=token,email=user.email)

