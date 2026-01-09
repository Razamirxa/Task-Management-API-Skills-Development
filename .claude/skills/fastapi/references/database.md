# FastAPI Database Integration

Complete guide to working with databases in FastAPI using SQLModel and SQLAlchemy.

## ORM Options

| Feature | SQLModel | SQLAlchemy |
|---------|----------|------------|
| Pydantic integration | Built-in | Separate schemas needed |
| Type hints | Native | Manual |
| Learning curve | Easier | Steeper |
| Flexibility | Good for most cases | Maximum control |
| Best for | FastAPI projects | Complex legacy systems |

**Recommendation:** Use **SQLModel** for new FastAPI projects (same author as FastAPI).

---

# SQLModel Integration (Recommended)

## Quick Start with Neon

### 1. Install Dependencies

```bash
pip install sqlmodel psycopg2-binary python-dotenv
# Or for async:
pip install sqlmodel asyncpg python-dotenv
```

### 2. Environment Setup

```bash
# .env
DATABASE_URL=postgresql://user:password@ep-cool-name-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
```

### 3. Database Connection (database.py)

```python
# database.py
import os
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection args for Neon (serverless PostgreSQL)
connect_args = {"sslmode": "require"}

engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set False in production
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before use
)

def create_db_and_tables():
    """Create all tables defined in SQLModel classes."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Yield database session with proper cleanup."""
    with Session(engine) as session:
        yield session
```

## SQLModel Table Definitions

### Basic Table Model

```python
# models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    """Base model with shared fields (not a table)."""
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    is_active: bool = Field(default=True)

class User(UserBase, table=True):
    """Database table model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

class UserCreate(UserBase):
    """Schema for creating users (request body)."""
    pass

class UserRead(UserBase):
    """Schema for reading users (response)."""
    id: int
    created_at: datetime

class UserUpdate(SQLModel):
    """Schema for updating users (all fields optional)."""
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
```

### Table with Relationships

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # One-to-many relationship
    members: List["Member"] = Relationship(back_populates="team")

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Many-to-one relationship
    team: Optional[Team] = Relationship(back_populates="members")
```

### Many-to-Many Relationships

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

# Link table for many-to-many
class BookAuthorLink(SQLModel, table=True):
    book_id: Optional[int] = Field(
        default=None, foreign_key="book.id", primary_key=True
    )
    author_id: Optional[int] = Field(
        default=None, foreign_key="author.id", primary_key=True
    )

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    authors: List["Author"] = Relationship(
        back_populates="books", link_model=BookAuthorLink
    )

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    books: List[Book] = Relationship(
        back_populates="authors", link_model=BookAuthorLink
    )
```

## Session Management

### Yield Dependency Pattern (Recommended)

```python
# database.py
from sqlmodel import Session, create_engine

def get_session():
    """
    Yield a database session.
    - Session is created when dependency is called
    - Session is automatically closed after request completes
    - Works with FastAPI's dependency injection
    """
    with Session(engine) as session:
        yield session
```

### Using in Routes

```python
from fastapi import FastAPI, Depends
from sqlmodel import Session
from database import get_session, create_db_and_tables

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/users/{user_id}")
def read_user(user_id: int, session: Session = Depends(get_session)):
    # Session is injected and managed automatically
    user = session.get(User, user_id)
    return user
```

### Context Manager Pattern (Manual Use)

```python
from sqlmodel import Session
from database import engine

# For scripts or background tasks
def process_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        for user in users:
            # Process user
            pass
        session.commit()
```

## CRUD Operations

### Complete CRUD Module

```python
# crud.py
from sqlmodel import Session, select
from models import User, UserCreate, UserUpdate
from typing import Optional, List
from datetime import datetime

# CREATE
def create_user(session: Session, user: UserCreate) -> User:
    """Create a new user."""
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# READ - Single
def get_user(session: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Get a user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

# READ - Multiple
def get_users(
    session: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """Get multiple users with pagination."""
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()

def get_active_users(session: Session) -> List[User]:
    """Get all active users."""
    statement = select(User).where(User.is_active == True)
    return session.exec(statement).all()

# UPDATE
def update_user(
    session: Session,
    user_id: int,
    user_update: UserUpdate
) -> Optional[User]:
    """Update a user."""
    db_user = session.get(User, user_id)
    if not db_user:
        return None

    # Only update provided fields
    user_data = user_update.model_dump(exclude_unset=True)
    for key, value in user_data.items():
        setattr(db_user, key, value)

    db_user.updated_at = datetime.utcnow()
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# DELETE
def delete_user(session: Session, user_id: int) -> bool:
    """Delete a user. Returns True if deleted, False if not found."""
    db_user = session.get(User, user_id)
    if not db_user:
        return False

    session.delete(db_user)
    session.commit()
    return True
```

### FastAPI Routes with CRUD

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session
from database import get_session, create_db_and_tables
from models import User, UserCreate, UserRead, UserUpdate
import crud

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    # Check if email already exists
    existing = crud.get_user_by_email(session, user.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return crud.create_user(session, user)

@app.get("/users/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    return crud.get_users(session, skip=skip, limit=limit)

@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session)
):
    user = crud.update_user(session, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    if not crud.delete_user(session, user_id):
        raise HTTPException(status_code=404, detail="User not found")
```

## Neon-Specific Configuration

### Connection URL Format

```python
# Neon PostgreSQL connection string format
DATABASE_URL = "postgresql://[user]:[password]@[endpoint].neon.tech/[database]?sslmode=require"

# Example:
DATABASE_URL = "postgresql://myuser:mypass@ep-cool-name-123456.us-east-2.aws.neon.tech/mydb?sslmode=require"
```

### Optimized Engine for Neon

```python
from sqlmodel import create_engine

# Neon is serverless - optimize for cold starts
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_pre_ping=True,  # Verify connection before use (handles serverless timeouts)
    pool_size=5,  # Smaller pool for serverless
    max_overflow=10,
    pool_recycle=300,  # Recycle connections every 5 minutes
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
    }
)
```

### Environment-Based Configuration

```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    echo_sql: bool = False

    class Config:
        env_file = ".env"

settings = Settings()

# database.py
from config import settings
from sqlmodel import create_engine

engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    pool_pre_ping=True,
)
```

## Advanced Query Patterns

### Filtering with SQLModel

```python
from sqlmodel import select, or_, and_

# Multiple conditions (AND)
statement = select(User).where(
    User.is_active == True,
    User.name.contains("John")
)

# OR conditions
statement = select(User).where(
    or_(
        User.email.endswith("@gmail.com"),
        User.email.endswith("@company.com")
    )
)

# Combined AND/OR
statement = select(User).where(
    and_(
        User.is_active == True,
        or_(
            User.name == "Alice",
            User.name == "Bob"
        )
    )
)
```

### Ordering and Pagination

```python
from sqlmodel import select

# Order by
statement = select(User).order_by(User.created_at.desc())

# Pagination
def get_paginated(session: Session, page: int = 1, per_page: int = 10):
    statement = (
        select(User)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return session.exec(statement).all()
```

### Eager Loading Relationships

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# Load team with all members in one query
statement = select(Team).options(selectinload(Team.members))
teams = session.exec(statement).all()

# Access members without additional queries
for team in teams:
    for member in team.members:
        print(member.name)
```

## Testing with SQLModel

```python
# conftest.py
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from main import app
from database import get_session

@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite for testing."""
    engine = create_engine(
        "sqlite://",  # In-memory database
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with overridden session."""
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

# test_users.py
def test_create_user(client):
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_read_user(client, session):
    # Create test user
    user = User(email="test@example.com", name="Test")
    session.add(user)
    session.commit()
    session.refresh(user)

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

---

# SQLAlchemy Integration (Alternative)

## Quick Start

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# models.py
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
```

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models import User

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()
```

## Database URLs

### SQLite
```python
DATABASE_URL = "sqlite:///./app.db"
# For async:
DATABASE_URL = "sqlite+aiosqlite:///./app.db"
```

### PostgreSQL
```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
# For async:
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"
```

### MySQL
```python
DATABASE_URL = "mysql://user:password@localhost/dbname"
# For async:
DATABASE_URL = "mysql+aiomysql://user:password@localhost/dbname"
```

## Models (SQLAlchemy)

### Basic Model

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Relationships

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

    # One-to-many
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Many-to-one
    owner = relationship("User", back_populates="items")
```

## CRUD Operations

### Create

```python
from sqlalchemy.orm import Session
from models import User

def create_user(db: Session, email: str, name: str):
    db_user = User(email=email, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Get the generated ID
    return db_user
```

### Read

```python
# Get one
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Get many
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

# With filtering
def get_users_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).all()
```

### Update

```python
def update_user(db: Session, user_id: int, name: str):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.name = name
        db.commit()
        db.refresh(db_user)
    return db_user
```

### Delete

```python
def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
```

## Async Database (Recommended for Production)

### Setup

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Async CRUD

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).filter(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, email: str, name: str):
    db_user = User(email=email, name=name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

### Async Routes

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

@app.get("/users/{user_id}")
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## Migrations with Alembic

### Setup

```bash
pip install alembic
alembic init alembic
```

### Configure Alembic

Edit `alembic/env.py`:

```python
from app.database import Base
from app.models import *  # Import all models

target_metadata = Base.metadata
```

Edit `alembic.ini`:

```ini
sqlalchemy.url = postgresql://user:pass@localhost/db
```

### Create Migration

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Create users table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Query Patterns

### Filtering

```python
# Multiple conditions
users = db.query(User).filter(
    User.email.like("%@example.com"),
    User.is_active == True
).all()

# OR conditions
from sqlalchemy import or_
users = db.query(User).filter(
    or_(User.email == "a@example.com", User.email == "b@example.com")
).all()
```

### Ordering

```python
users = db.query(User).order_by(User.created_at.desc()).all()
```

### Joining

```python
items_with_owners = db.query(Item).join(User).all()

# With filtering
items = db.query(Item).join(User).filter(User.email == "a@example.com").all()
```

### Pagination

```python
def get_paginated_users(db: Session, page: int = 1, per_page: int = 10):
    skip = (page - 1) * per_page
    return db.query(User).offset(skip).limit(per_page).all()
```

### Count

```python
total_users = db.query(User).count()
active_users = db.query(User).filter(User.is_active == True).count()
```

## Connection Pooling

```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Number of connections to keep
    max_overflow=20,        # Extra connections if needed
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True      # Verify connection before use
)
```

## Testing with Databases

### Use Test Database

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture
def test_db():
    engine = create_engine(TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

---

# Best Practices

1. **Use dependency injection** - Always use `Depends(get_session)` for sessions
2. **Close sessions properly** - Use context managers or try/finally
3. **Use indexes** - Add indexes to frequently queried columns
4. **Use SQLModel for FastAPI** - Better Pydantic integration, less boilerplate
5. **Use async for production** - Better performance with async database drivers
6. **Use migrations** - Never modify tables manually, use Alembic
7. **Connection pooling** - Configure pool size based on load
8. **Environment variables** - Never hardcode database credentials
9. **Use transactions** - Wrap related operations in transactions
10. **Test with real database** - Don't mock database in integration tests

## Common Pitfalls

- **Not closing sessions** - Always use dependency injection or context managers
- **N+1 queries** - Use `selectinload()` to eager load relationships
- **Missing indexes** - Add indexes to foreign keys and frequently filtered columns
- **Hardcoded credentials** - Use environment variables
- **Not using migrations** - Always use Alembic for schema changes
- **Blocking I/O** - Use async for production applications
- **Neon cold starts** - Use `pool_pre_ping=True` to handle connection timeouts
