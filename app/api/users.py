from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.models.models import User
from app.models.schemas import UserResponse, UserCreate, UserUpdate
from app.core.database import get_session
from app.core.auth import get_password_hash

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    session: Session = Depends(get_session)
):
    query = select(User)
    if active_only:
        query = query.where(User.is_active == True)
    users = session.exec(query.offset(skip).limit(limit)).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.version != db_user.version:
        raise HTTPException(status_code=409, detail="Concurrent modification detected")
    
    user_data = user_update.dict(exclude_unset=True, exclude={"version"})
    user_data["version"] = db_user.version + 1
    
    for key, value in user_data.items():
        setattr(db_user, key, value)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    session.add(user)
    session.commit()
    return {"message": "User deactivated"}