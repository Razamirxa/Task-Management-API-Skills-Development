#!/usr/bin/env python3
"""
Add Database Support to FastAPI Project

Adds database configuration files for SQLAlchemy.

Usage:
    python add_database.py [--db-type TYPE] [--output-dir DIR]

Examples:
    python add_database.py --db-type postgresql
    python add_database.py --db-type sqlite --output-dir ./my-project
"""

import argparse
from pathlib import Path


DATABASE_TEMPLATE = '''"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - change this for your database
# SQLite: sqlite:///./{{PROJECT_NAME}}.db
# PostgreSQL: postgresql://user:password@localhost/dbname
# MySQL: mysql://user:password@localhost/dbname
SQLALCHEMY_DATABASE_URL = "{{DATABASE_URL}}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    {{CONNECT_ARGS}}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''

MODELS_TEMPLATE = '''"""
Database models.

Example model - customize as needed.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from .database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''

REQUIREMENTS_TEMPLATES = {
    'sqlite': 'sqlalchemy==2.0.23\n',
    'postgresql': 'sqlalchemy==2.0.23\npsycopg2-binary==2.9.9\n',
    'mysql': 'sqlalchemy==2.0.23\npymysql==1.1.0\n'
}

DATABASE_URLS = {
    'sqlite': 'sqlite:///./{{PROJECT_NAME}}.db',
    'postgresql': 'postgresql://user:password@localhost/{{PROJECT_NAME}}',
    'mysql': 'mysql://user:password@localhost/{{PROJECT_NAME}}'
}

CONNECT_ARGS = {
    'sqlite': 'connect_args={"check_same_thread": False}',
    'postgresql': '',
    'mysql': ''
}


def add_database(db_type: str, output_dir: str, project_name: str = "app"):
    """Add database configuration to a FastAPI project."""

    output_path = Path(output_dir)

    if not output_path.exists():
        print(f"Error: Directory '{output_path}' does not exist")
        return

    # Get database-specific values
    db_url = DATABASE_URLS.get(db_type, DATABASE_URLS['sqlite'])
    connect_args = CONNECT_ARGS.get(db_type, '')

    # Create database.py
    db_content = DATABASE_TEMPLATE.replace('{{DATABASE_URL}}', db_url)
    db_content = db_content.replace('{{CONNECT_ARGS}}', connect_args)
    db_content = db_content.replace('{{PROJECT_NAME}}', project_name)

    db_file = output_path / "database.py"
    print(f"Creating {db_file}...")
    db_file.write_text(db_content, encoding='utf-8')

    # Create models.py
    models_file = output_path / "models.py"
    print(f"Creating {models_file}...")
    models_file.write_text(MODELS_TEMPLATE, encoding='utf-8')

    # Create requirements snippet
    req_snippet = output_path / "database_requirements.txt"
    print(f"Creating {req_snippet}...")
    req_snippet.write_text(REQUIREMENTS_TEMPLATES[db_type], encoding='utf-8')

    # Create init script
    init_script = output_path / "init_db.py"
    init_content = '''"""Initialize database tables."""
from database import engine, Base
from models import *  # Import all models

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
'''
    print(f"Creating {init_script}...")
    init_script.write_text(init_content, encoding='utf-8')

    print("\n✅ Database configuration added successfully!")
    print(f"\nDatabase type: {db_type}")
    print(f"Database URL: {db_url}")
    print("\nNext steps:")
    print(f"  1. Install dependencies:")
    print(f"     pip install {REQUIREMENTS_TEMPLATES[db_type].strip().replace(chr(10), ' ')}")
    print(f"\n  2. Update database URL in database.py with your credentials")
    print(f"\n  3. Define your models in models.py")
    print(f"\n  4. Initialize database:")
    print(f"     python init_db.py")
    print(f"\n  5. Use the database in your routes:")
    print(f"     from database import get_db")
    print(f"     from sqlalchemy.orm import Session")
    print(f"     @app.get('/items')")
    print(f"     def get_items(db: Session = Depends(get_db)):")
    print(f"         return db.query(Item).all()")


def main():
    parser = argparse.ArgumentParser(
        description="Add database support to FastAPI project"
    )

    parser.add_argument(
        "--db-type",
        choices=['sqlite', 'postgresql', 'mysql'],
        default='sqlite',
        help="Database type (default: sqlite)"
    )

    parser.add_argument(
        "--output-dir",
        default=".",
        help="Project directory (default: current directory)"
    )

    parser.add_argument(
        "--project-name",
        default="app",
        help="Project name for database naming (default: app)"
    )

    args = parser.parse_args()
    add_database(args.db_type, args.output_dir, args.project_name)


if __name__ == "__main__":
    main()
