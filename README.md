# Task Management System

## Overview
A web-based task management application built with modern technologies. The system allows users to create, manage, and track tasks within projects, with role-based access control and authentication.

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - Database ORM with type safety
- **PostgreSQL** - Relational database
- **JWT** - Token-based authentication
- **Pydantic** - Data validation and serialization

### Frontend
- **HTML/CSS/JavaScript** - Vanilla web technologies
- **Bootstrap 5** - UI framework
- **Fetch API** - HTTP client for API calls

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
├── main.py                 # Application entry point
├── app/
│   ├── core/               # Configuration and database
│   ├── models/             # Data models and schemas
│   └── api/                # REST API endpoints
├── static/                 # Frontend assets
└── templates/              # HTML templates
```

### Key Features
- User authentication and authorization (Admin/Regular roles)
- Project and task management with CRUD operations
- Task labeling and filtering
- Bulk operations
- RESTful API with OpenAPI documentation
- Responsive web interface
- Optimistic locking for concurrent updates

### Data Models
- **Users** - Authentication and role management
- **Projects** - Container for tasks with ownership
- **Tasks** - Work items with status, priority, and assignments
- **Labels** - Categorization tags for tasks

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed

### Running the Application
1. Clone the repository
2. Navigate to the project directory
3. Start the application:
   ```bash
   docker-compose up --build
   ```
4. Access the application at http://localhost:8000

### Available Endpoints
- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Login Page:** http://localhost:8000/login
- **User Dashboard:** http://localhost:8000/dashboard (requires login)
- **Admin Panel:** http://localhost:8000/admin (requires admin role)

## Test Data

The application automatically seeds test data on startup:

### User Accounts
- **Admin User:** `admin@example.com` / `admin123`
- **Regular User:** `john@example.com` / `user123`
- **Regular User:** `jane@example.com` / `user123`

### Sample Data
- Multiple projects with different owners
- Tasks with various statuses (todo, in_progress, done)
- Tasks with different priorities (low, medium, high)
- Labels for categorization
- Task assignments and label relationships

## API Structure

The REST API follows standard conventions:
- **Base URL:** `/api/v1`
- **Authentication:** Bearer token (JWT)
- **Content-Type:** `application/json`
- **Status Codes:** Standard HTTP response codes

### Main Endpoints
- `/api/v1/auth/*` - Authentication and authorization
- `/api/v1/users/*` - User management
- `/api/v1/projects/*` - Project operations
- `/api/v1/tasks/*` - Task management
- `/api/v1/labels/*` - Label operations

For complete API documentation, visit http://localhost:8000/docs after starting the application.