from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from app.models.models import Project, User
from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(project: Project, session: Session = Depends(get_session)):
    owner = session.get(User, project.owner_id)
    if not owner:
        raise HTTPException(status_code=400, detail="Owner not found")
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = 0, 
    limit: int = 100,
    owner_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(Project).where(Project.is_active == True)
    if owner_id:
        query = query.where(Project.owner_id == owner_id)
    projects = session.exec(query.offset(skip).limit(limit)).all()
    return projects

@router.get("/{project_id}", response_model=Project)
def read_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project or not project.is_active:
        raise HTTPException(status_code=404, detail="Project not found")
    return project