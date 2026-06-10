from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.dependencies import get_current_user
from app.models import User
from app.schemas import RegisterRequest, RegisterResponse, LoginRequest, TokenResponse, OTPVerifyRequest, RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest, UserResponse

import httpx
from urllib.parse import urlencode
from passlib.context import CryptContext
from app.jwt_handler import create_access_token, create_refresh_token
import random
import secrets
import string
from datetime import datetime, timedelta, timezone
from app.email_service import send_otp_email, send_password_reset_email
from jose import JWTError
from app.jwt_handler import create_access_token, create_refresh_token, decode_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    
    # Step 1 — password match check
    if payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Step 2 — email already exists?
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Step 3 — password hash karo
    hashed_password = pwd_context.hash(payload.password)
    
    # Step 4 — user banao
    new_user = User(
        email=payload.email,
        password_hash=hashed_password
    )
    
    # Step 5 — database mein save karo
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    # Step 6 — OTP aur verification_token generate karo
    otp = "".join(random.choices(string.digits, k=6))
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    verification_token = secrets.token_urlsafe(32)

    # Step 7 — Database mein save karo
    new_user.otp_code = otp
    new_user.otp_expiry = otp_expiry
    new_user.verification_token = verification_token
    db.commit()

    # Step 8 — Email bhejo
    send_otp_email(new_user.email, otp)

    # Step 9 — verification_token return karo
    return RegisterResponse(
        verification_token=verification_token,
        message="OTP sent to your email. Please verify within 10 minutes."
    )



@router.post("/login", status_code=200)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    
    # Step 1 — email check
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered"
        )
    
    # Step 2 — password check
    if not pwd_context.verify(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Step 3 — verified check
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    
    # Step 4 — tokens banao
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    
    # Step 5 — HttpOnly cookies set karo
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800
    )
    
    return {"message": "Login successful"}


@router.post("/verify-otp", status_code=200)
def verify_otp(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    
    # Step 1 — verification_token se user dhundho
    user = db.query(User).filter(
        User.verification_token == payload.verification_token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token"
        )
    
    # Step 2 — OTP expire check
    if datetime.now(timezone.utc) > user.otp_expiry.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please register again."
        )
    
    # Step 3 — OTP match karo
    if user.otp_code != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Step 4 — verify karo aur token clean karo
    user.is_verified = True
    user.otp_code = None
    user.otp_expiry = None
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully. You can now login."}

@router.post("/refresh-token", status_code=200)
def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    
    try:
        data = decode_token(refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    if data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user = db.query(User).filter(User.id == data.get("user_id")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Naye tokens banao
    new_access_token = create_access_token({"user_id": user.id})
    new_refresh_token = create_refresh_token({"user_id": user.id})
    
    # Cookies update karo
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=604800
    )
    
    return {"message": "Tokens refreshed successfully"}

@router.post("/forgot-password", status_code=200)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    
    # Step 1 — email check karo
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered"
        )
    
    # Step 2 — OTP aur verification_token generate karo
    otp = "".join(random.choices(string.digits, k=6))
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    verification_token = secrets.token_urlsafe(32)
    
    # Step 3 — database mein save karo
    user.otp_code = otp
    user.otp_expiry = otp_expiry
    user.verification_token = verification_token
    db.commit()
    
    # Step 4 — email bhejo
    send_password_reset_email(user.email, otp)
    
    return {
        "verification_token": verification_token,
        "message": "OTP sent to your email."
    }


@router.post("/reset-password", status_code=200)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    
    # Step 1 — verification_token se user dhundho
    user = db.query(User).filter(
        User.verification_token == payload.verification_token
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification token"
        )
    
    # Step 2 — OTP expire check
    if datetime.now(timezone.utc) > user.otp_expiry.replace(tzinfo=timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please try again."
        )
    
    # Step 3 — OTP match karo
    if user.otp_code != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Step 4 — password match karo
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Step 5 — naya password hash karke save karo
    user.password_hash = pwd_context.hash(payload.new_password)
    user.otp_code = None
    user.otp_expiry = None
    user.verification_token = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now login."}


@router.get("/google/login")
def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return {"url": google_auth_url}


@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)):
    
    # Step 1 — code se Google access token lo
    token_response = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    )
    token_data = token_response.json()
    
    if "error" in token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google authentication failed"
        )
    
    # Step 2 — Google se user info lo
    user_info_response = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {token_data['access_token']}"}
    )
    user_info = user_info_response.json()
    
    # Step 3 — user exist karta hai?
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    # Step 4 — nahi karta toh banao
    if not user:
        user = User(
            email=user_info["email"],
            password_hash="GOOGLE_AUTH",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Step 5 — tokens banao
    access_token = create_access_token({"user_id": user.id})
    refresh_token = create_refresh_token({"user_id": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )



@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout", status_code=200)
def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}