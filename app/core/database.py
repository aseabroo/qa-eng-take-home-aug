from sqlmodel import SQLModel, create_engine, Session, select
from app.core.config import settings
import time
import logging

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

def create_db_and_tables():
    max_retries = 30
    for attempt in range(max_retries):
        try:
            # Drop all tables and recreate them (for development)
            SQLModel.metadata.drop_all(engine)
            SQLModel.metadata.create_all(engine)
            logging.info("Database tables created successfully")
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            logging.warning(f"Database connection attempt {attempt + 1} failed, retrying in 2 seconds...")
            time.sleep(2)

def seed_initial_data():
    """Seed initial data if it doesn't exist"""
    with Session(engine) as session:
        try:
            from app.models.models import User
            from app.models.enums import UserRole
            from app.core.auth import get_password_hash
            
            # Check if data already exists
            existing_users = session.exec(select(User)).first()
            if existing_users:
                logging.info("Initial data already exists, skipping seeding")
                return
            
            logging.info("Seeding initial data...")
            
            # Import here to avoid circular imports
            from seed_data import seed_test_data
            seed_test_data()
            
            logging.info("Initial data seeded successfully")
            
        except Exception as e:
            logging.error(f"Error seeding initial data: {e}")
            # Don't raise the exception to prevent startup failure

def get_session():
    with Session(engine) as session:
        yield session