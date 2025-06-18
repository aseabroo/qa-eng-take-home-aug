from sqlmodel import Session, select
from app.core.database import engine
from app.models.models import User, Project, Task, Label, TaskLabelLink
from app.models.enums import UserRole, TaskStatus, TaskPriority
from datetime import datetime, timedelta
import os

db_host = os.getenv("DB_HOST", "localhost" if os.getenv("ENV") == "test" else "db")

DATABASE_URL = f"postgresql://postgres:password@{db_host}:5432/postgres"

def seed_test_data():
    from app.core.auth import get_password_hash
    
    with Session(engine) as session:
        # Check if users already exist
        existing_admin = session.exec(select(User).where(User.email == "admin@example.com")).first()
        if existing_admin:
            print("Test users already exist, skipping user creation")
            admin_user = existing_admin
            regular_user1 = session.exec(select(User).where(User.email == "john@example.com")).first()
            regular_user2 = session.exec(select(User).where(User.email == "jane@example.com")).first()
        else:
            # Create users with hashed passwords
            admin_user = User(
                email="admin@example.com",
                name="Admin User",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN
            )
            
            regular_user1 = User(
                email="john@example.com",
                name="John Doe",
                password_hash=get_password_hash("user123"),
                role=UserRole.REGULAR
            )
            
            regular_user2 = User(
                email="jane@example.com",
                name="Jane Smith",
                password_hash=get_password_hash("user123"),
                role=UserRole.REGULAR
            )
            
            session.add_all([admin_user, regular_user1, regular_user2])
            session.commit()
            session.refresh(admin_user)
            session.refresh(regular_user1)
            session.refresh(regular_user2)
            print("Test users created successfully")
        
        # Create labels (check if they exist first)
        existing_labels = session.exec(select(Label)).all()
        if not existing_labels:
            labels = [
                Label(name="Frontend", color="#007bff"),
                Label(name="Backend", color="#28a745"),
                Label(name="Bug", color="#dc3545"),
                Label(name="Feature", color="#ffc107"),
                Label(name="Urgent", color="#fd7e14")
            ]
            session.add_all(labels)
            session.commit()
            print("Test labels created successfully")
        else:
            labels = existing_labels
            print("Test labels already exist, skipping label creation")
        
        # Create projects (check if they exist first)
        existing_projects = session.exec(select(Project)).all()
        if not existing_projects:
            project1 = Project(
                name="E-commerce Platform",
                description="Building a modern e-commerce platform",
                owner_id=admin_user.id
            )
            
            project2 = Project(
                name="Mobile App",
                description="Developing mobile application",
                owner_id=regular_user1.id
            )
            
            session.add_all([project1, project2])
            session.commit()
            session.refresh(project1)
            session.refresh(project2)
            print("Test projects created successfully")
        else:
            project1 = existing_projects[0]
            project2 = existing_projects[1] if len(existing_projects) > 1 else existing_projects[0]
            print("Test projects already exist, skipping project creation")
        
        # Create tasks (check if they exist first)
        existing_tasks = session.exec(select(Task)).all()
        if not existing_tasks:
            tasks = [
                Task(
                    title="Implement user authentication",
                    description="Add JWT-based authentication system",
                    status=TaskStatus.IN_PROGRESS,
                    priority=TaskPriority.HIGH,
                    project_id=project1.id,
                    assigned_to_id=regular_user1.id,
                    due_date=datetime.utcnow() + timedelta(days=7)
                ),
                Task(
                    title="Design product catalog UI",
                    description="Create responsive product listing page",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.MEDIUM,
                    project_id=project1.id,
                    assigned_to_id=regular_user2.id,
                    due_date=datetime.utcnow() + timedelta(days=10)
                ),
                Task(
                    title="Fix shopping cart bug",
                    description="Cart items disappearing on page refresh",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.HIGH,
                    project_id=project1.id,
                    assigned_to_id=regular_user1.id,
                    due_date=datetime.utcnow() + timedelta(days=3)
                ),
                Task(
                    title="Implement push notifications",
                    description="Add FCM integration for mobile app",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.LOW,
                    project_id=project2.id,
                    assigned_to_id=regular_user2.id,
                    due_date=datetime.utcnow() + timedelta(days=14)
                ),
                Task(
                    title="Performance optimization",
                    description="Optimize app loading time",
                    status=TaskStatus.DONE,
                    priority=TaskPriority.MEDIUM,
                    project_id=project2.id,
                    assigned_to_id=regular_user1.id
                )
            ]
            
            session.add_all(tasks)
            session.commit()
            print("Test tasks created successfully")
        else:
            tasks = existing_tasks
            print("Test tasks already exist, skipping task creation")
        
        # Assign labels to tasks (check if they exist first)
        existing_links = session.exec(select(TaskLabelLink)).all()
        if not existing_links and len(tasks) >= 5 and len(labels) >= 5:
            task_label_links = [
                TaskLabelLink(task_id=tasks[0].id, label_id=labels[1].id),  # Backend
                TaskLabelLink(task_id=tasks[0].id, label_id=labels[3].id),  # Feature
                TaskLabelLink(task_id=tasks[1].id, label_id=labels[0].id),  # Frontend
                TaskLabelLink(task_id=tasks[1].id, label_id=labels[3].id),  # Feature
                TaskLabelLink(task_id=tasks[2].id, label_id=labels[2].id),  # Bug
                TaskLabelLink(task_id=tasks[2].id, label_id=labels[4].id),  # Urgent
                TaskLabelLink(task_id=tasks[3].id, label_id=labels[3].id),  # Feature
                TaskLabelLink(task_id=tasks[4].id, label_id=labels[1].id),  # Backend
            ]
            
            session.add_all(task_label_links)
            session.commit()
            print("Task-label relationships created successfully")
        else:
            print("Task-label relationships already exist or insufficient data, skipping")
        
        print("Initial data seeding completed!")
        user_count = len(session.exec(select(User)).all())
        label_count = len(session.exec(select(Label)).all())
        project_count = len(session.exec(select(Project)).all())
        task_count = len(session.exec(select(Task)).all())
        print(f"Database contains: {user_count} users, {label_count} labels, {project_count} projects, {task_count} tasks")

if __name__ == "__main__":
    seed_test_data()