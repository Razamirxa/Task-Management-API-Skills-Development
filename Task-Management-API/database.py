"""
Database Configuration for Neon PostgreSQL

Uses SQLModel with dependency injection pattern for FastAPI.
The get_session function yields a database session that is
automatically closed after each request.
"""

import os
from urllib.parse import unquote
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment and decode URL-encoded characters
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please create a .env file with your Neon connection string."
    )

# Decode URL-encoded characters (e.g., %20 -> space)
DATABASE_URL = unquote(DATABASE_URL)

# Create engine with Neon-optimized settings
# - pool_pre_ping: Verifies connection before use (handles serverless timeouts)
# - echo: Set to True for SQL debugging, False in production
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Important for Neon serverless
)


def create_db_and_tables():
    """
    Create all database tables defined in SQLModel classes.
    Called on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency injection function for database sessions.

    Yields a Session that is automatically closed after the request.
    Use with FastAPI's Depends():

        @app.get("/items")
        def get_items(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
