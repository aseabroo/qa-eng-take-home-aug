from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from app.models.enums import UserRole, TaskStatus, TaskPriority

class TaskLabelLink(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    label_id: Optional[int] = Field(default=None, foreign_key="label.id", primary_key=True)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: str
    role: UserRole = Field(default=UserRole.REGULAR)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)
    
    projects: List["Project"] = Relationship(back_populates="owner")

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    version: int = Field(default=1)
    
    owner: User = Relationship(back_populates="projects")
    tasks: List["Task"] = Relationship(back_populates="project")

class Label(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    color: str = Field(default="#007bff")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    tasks: List["Task"] = Relationship(back_populates="labels", link_model=TaskLabelLink)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    project_id: int = Field(foreign_key="project.id")
    assigned_to_id: Optional[int] = Field(default=None, foreign_key="user.id")
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)
    
    project: Project = Relationship(back_populates="tasks")
    assigned_to: Optional[User] = Relationship()
    labels: List[Label] = Relationship(back_populates="tasks", link_model=TaskLabelLink)