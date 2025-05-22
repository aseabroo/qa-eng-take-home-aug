from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.core.auth import authenticate_user, create_access_token, get_current_active_user, require_admin
from app.core.config import settings
from app.core.database import get_session
from app.models.schemas import Token, UserResponse
from app.models.models import User

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    return {
        "message": f"Hello {current_user.name}! This is a protected route.",
        "user_role": current_user.role,
        "access_level": "authenticated"
    }

@router.get("/admin-only")
async def admin_only_route(current_user: User = Depends(require_admin)):
    return {
        "message": f"Hello Admin {current_user.name}! This is an admin-only route.",
        "user_role": current_user.role,
        "access_level": "admin"
    }