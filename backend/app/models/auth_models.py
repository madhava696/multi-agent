from pydantic import BaseModel,EmailStr,Field
from typing import Literal

class RegisterRequest(BaseModel):
    email : EmailStr
    password : str = Field(min_length=6)

class LoginRequest(BaseModel):
    email : EmailStr
    password : str = Field(min_length=6)

class TokenResponse(BaseModel):
    access_token : str
    token_type : str = Literal["bearer"]   
    email : EmailStr

class UserResponse(BaseModel):
    email : EmailStr