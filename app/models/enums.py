from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    REGULAR = "regular"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"