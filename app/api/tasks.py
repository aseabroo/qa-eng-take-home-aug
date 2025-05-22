from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models.models import Task, Project, User
from app.models.enums import TaskStatus, TaskPriority
from app.core.database import get_session

router = APIRouter()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: Task, session: Session = Depends(get_session)):
    project = session.get(Project, task.project_id)
    if not project:
        raise HTTPException(status_code=400, detail="Project not found")
    if task.assigned_to_id:
        user = session.get(User, task.assigned_to_id)
        if not user:
            raise HTTPException(status_code=400, detail="Assigned user not found")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/", response_model=List[Task])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    status_filter: Optional[TaskStatus] = None,
    priority_filter: Optional[TaskPriority] = None,
    assigned_to_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(Task)
    if project_id:
        query = query.where(Task.project_id == project_id)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if priority_filter:
        query = query.where(Task.priority == priority_filter)
    if assigned_to_id:
        query = query.where(Task.assigned_to_id == assigned_to_id)
    
    tasks = session.exec(query.offset(skip).limit(limit)).all()
    return tasks

@router.get("/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: Task, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.version != db_task.version:
        raise HTTPException(status_code=409, detail="Concurrent modification detected")
    
    task_data = task_update.dict(exclude_unset=True, exclude={"id"})
    task_data["version"] = db_task.version + 1
    task_data["updated_at"] = datetime.utcnow()
    
    for key, value in task_data.items():
        setattr(db_task, key, value)
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@router.delete("/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"message": "Task deleted"}

@router.delete("/bulk")
def bulk_delete_tasks(task_ids: List[int], session: Session = Depends(get_session)):
    deleted_count = 0
    for task_id in task_ids:
        task = session.get(Task, task_id)
        if task:
            session.delete(task)
            deleted_count += 1
    session.commit()
    return {"deleted_count": deleted_count}

@router.put("/bulk/status")
def bulk_update_task_status(
    task_ids: List[int], 
    new_status: TaskStatus, 
    session: Session = Depends(get_session)
):
    updated_count = 0
    for task_id in task_ids:
        task = session.get(Task, task_id)
        if task:
            task.status = new_status
            task.updated_at = datetime.utcnow()
            updated_count += 1
    session.commit()
    return {"updated_count": updated_count}