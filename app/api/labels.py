from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from app.models.models import Label
from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=Label, status_code=status.HTTP_201_CREATED)
def create_label(label: Label, session: Session = Depends(get_session)):
    db_label = session.exec(select(Label).where(Label.name == label.name)).first()
    if db_label:
        raise HTTPException(status_code=400, detail="Label already exists")
    session.add(label)
    session.commit()
    session.refresh(label)
    return label

@router.get("/", response_model=List[Label])
def read_labels(session: Session = Depends(get_session)):
    labels = session.exec(select(Label)).all()
    return labels