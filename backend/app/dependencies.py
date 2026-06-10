from fastapi import Depends, HTTPException, status, Cookie
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.jwt_handler import decode_token
from app.models import User
from typing import Optional

def get_current_user(
    access_token: Optional[str] = Cookie(default=None),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not access_token:
        raise credentials_exception
    
    try:
        data = decode_token(access_token)
    except JWTError:
        raise credentials_exception
    
    if data.get("type") != "access":
        raise credentials_exception
    
    user = db.query(User).filter(User.id == data.get("user_id")).first()
    if not user:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return user