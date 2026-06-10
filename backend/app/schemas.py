from datetime import datetime

from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: str
    email: str
    is_verified: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

        
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str



class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RegisterResponse(BaseModel):
    verification_token: str
    message: str

class OTPVerifyRequest(BaseModel):
    verification_token: str
    otp: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    verification_token: str
    otp: str
    new_password: str
    confirm_password: str