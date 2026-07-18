import json 
from typing import Optional
from fastapi import HTTPException,status

from app.memory.redis_memory import RedisMemoryService
from app.models.auth_models import *
from app.utils.security import *

class AuthService:
    def __init__(self,memory_service:RedisMemoryService):
        self.memory_service= memory_service

    def resgister_user(self,request:RegisterRequest)->UserResponse:
        key = self.memory_service.user_key(request.email)
        
        is_existing = self.memory_service.get_value(key)

        if is_existing:
            raise ValueError("USER ALREADY REGISTERED")
        
        payload = {
            "email":request.email,
            "hashed_password":hash_password(request.password)
        }

        self.memory_service.set_value(key,json.dumps(payload),ttl=-1)
        
        return UserResponse(email=request.email)
    
    def authenticate_user(self, request: LoginRequest) -> Optional[UserResponse] :
        key = self.memory_service.user_key(request.email)
        
        stored_user = self.memory_service.get_value(key)
        if not stored_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="USER NOT FOUND")

        payload = json. loads(stored_user)
        if not verify_password(request.password, payload["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="INVALID CREDENTIALS",headers="WWW-Authenticate")
        
        return UserResponse(email=request.email)
    
