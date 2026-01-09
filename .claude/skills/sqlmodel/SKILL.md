---
name: sqlmodel
description: SQLModel ORM skill for Python database operations. Use when defining database models, creating tables, managing sessions, writing CRUD operations, or integrating with FastAPI. Triggers include "create model", "database table", "SQLModel", "ORM", "session management", or "CRUD operations".
---

# SQLModel ORM Skill

SQLModel combines SQLAlchemy and Pydantic for Python database operations with type safety.

## Quick Start

### Installation

```bash
pip install sqlmodel
# For PostgreSQL:
pip install psycopg2-binary
# For async:
pip install asyncpg
```

### Basic Setup

```python
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional

# Define a model
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)

# Create engine and tables
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

# Use sessions for database operations
with Session(engine) as session:
    user = User(name="John", email="john@example.com")
    session.add(user)
    session.commit()
```

## Model Definitions

### Table Model (database table)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Item(SQLModel, table=True):
    """Database table - note table=True"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(ge=0)  # Greater than or equal to 0
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Schema Models (request/response)

```python
# Base with shared fields (NOT a table)
class ItemBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float

# Table model
class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Create schema (request body)
class ItemCreate(ItemBase):
    pass

# Read schema (response)
class ItemRead(ItemBase):
    id: int

# Update schema (partial)
class ItemUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
```

### Relationships

```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # One-to-many
    members: List["Member"] = Relationship(back_populates="team")

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Many-to-one
    team: Optional[Team] = Relationship(back_populates="members")
```

### Many-to-Many

```python
# Link table
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

## Database Connection

### SQLite

```python
engine = create_engine(
    "sqlite:///database.db",
    connect_args={"check_same_thread": False}  # Required for SQLite
)
```

### PostgreSQL (Neon)

```python
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,  # Important for serverless
)
```

### Create Tables

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

## Session Management

### Context Manager (Recommended)

```python
from sqlmodel import Session

def get_session():
    """Yield session with automatic cleanup."""
    with Session(engine) as session:
        yield session
```

### FastAPI Dependency Injection

```python
from fastapi import Depends

@app.get("/items/")
def read_items(session: Session = Depends(get_session)):
    items = session.exec(select(Item)).all()
    return items
```

## CRUD Operations

### Create

```python
def create_item(session: Session, item: ItemCreate) -> Item:
    db_item = Item.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

### Read

```python
from sqlmodel import select

# Get by ID
def get_item(session: Session, item_id: int) -> Optional[Item]:
    return session.get(Item, item_id)

# Get all with pagination
def get_items(session: Session, skip: int = 0, limit: int = 100) -> List[Item]:
    statement = select(Item).offset(skip).limit(limit)
    return session.exec(statement).all()

# Get with filter
def get_active_items(session: Session) -> List[Item]:
    statement = select(Item).where(Item.is_active == True)
    return session.exec(statement).all()
```

### Update

```python
def update_item(session: Session, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
    db_item = session.get(Item, item_id)
    if not db_item:
        return None

    # Only update provided fields
    item_data = item_update.model_dump(exclude_unset=True)
    for key, value in item_data.items():
        setattr(db_item, key, value)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
```

### Delete

```python
def delete_item(session: Session, item_id: int) -> bool:
    db_item = session.get(Item, item_id)
    if not db_item:
        return False

    session.delete(db_item)
    session.commit()
    return True
```

## Query Patterns

### Filtering

```python
from sqlmodel import select, or_, and_

# Single condition
statement = select(Item).where(Item.price > 100)

# Multiple conditions (AND)
statement = select(Item).where(
    Item.price > 100,
    Item.is_active == True
)

# OR conditions
statement = select(Item).where(
    or_(Item.name == "A", Item.name == "B")
)

# Combined
statement = select(Item).where(
    and_(
        Item.is_active == True,
        or_(Item.price < 10, Item.price > 100)
    )
)
```

### Ordering

```python
# Ascending
statement = select(Item).order_by(Item.price)

# Descending
statement = select(Item).order_by(Item.price.desc())

# Multiple
statement = select(Item).order_by(Item.is_active.desc(), Item.name)
```

### Pagination

```python
def get_paginated(session: Session, page: int = 1, per_page: int = 10):
    statement = (
        select(Item)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return session.exec(statement).all()
```

### Eager Loading

```python
from sqlalchemy.orm import selectinload

statement = select(Team).options(selectinload(Team.members))
teams = session.exec(statement).all()
```

## Testing

```python
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

@pytest.fixture
def session():
    """In-memory SQLite for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session
```

## Best Practices

1. **Separate table and schema models** - Use inheritance for DRY code
2. **Use `table=True`** - Only on actual database tables
3. **Optional IDs** - Set `id: Optional[int] = Field(default=None, primary_key=True)`
4. **Yield sessions** - Use context managers for automatic cleanup
5. **Use `model_validate()`** - Convert schemas to table models
6. **Use `model_dump(exclude_unset=True)`** - For partial updates
7. **Add indexes** - On frequently queried columns
8. **Use `pool_pre_ping=True`** - For serverless databases

## Common Pitfalls

- **Forgetting `table=True`** - Model won't create a table
- **Not refreshing after commit** - Won't have auto-generated fields
- **Not closing sessions** - Use context managers
- **N+1 queries** - Use `selectinload()` for relationships

## References

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [references/relationships.md](references/relationships.md) - Relationship patterns
- [references/migrations.md](references/migrations.md) - Alembic migrations
