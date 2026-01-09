# FastAPI Project Structure

Best practices for organizing FastAPI applications from small to large scale.

## Basic Structure (Small Projects)

For simple APIs with few endpoints:

```
my-api/
├── main.py           # Application entry point
├── models.py         # Database models
├── schemas.py        # Pydantic schemas
├── database.py       # Database configuration
├── requirements.txt  # Dependencies
└── .env             # Environment variables
```

**main.py example:**
```python
from fastapi import FastAPI
from database import engine, Base
from routers import items

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="My API", version="1.0.0")

# Include routers
app.include_router(items.router)

@app.get("/")
def root():
    return {"message": "Welcome to My API"}
```

## Medium Structure (Growing Projects)

For APIs with multiple resources and features:

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app instance
│   ├── config.py         # Configuration and settings
│   ├── database.py       # Database setup
│   ├── models/           # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── routers/          # API routes
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── items.py
│   └── dependencies.py   # Shared dependencies
├── tests/                # Test files
│   ├── __init__.py
│   └── test_items.py
├── requirements.txt
├── .env
└── README.md
```

## Advanced Structure (Large Projects)

For production applications with multiple modules:

```
my-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── core/             # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py   # Auth, encryption
│   │   └── config.py     # Configuration
│   ├── models/           # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── crud/             # Database operations
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── api/              # API routes
│   │   ├── __init__.py
│   │   ├── deps.py       # Dependencies
│   │   └── v1/           # API version 1
│   │       ├── __init__.py
│   │       ├── router.py
│   │       ├── users.py
│   │       └── items.py
│   ├── services/         # Business logic
│   │   ├── __init__.py
│   │   └── email.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Pytest fixtures
│   ├── test_api/
│   │   ├── test_users.py
│   │   └── test_items.py
│   └── test_services/
├── alembic/              # Database migrations
│   ├── versions/
│   └── env.py
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Key Files Explained

### main.py

Application entry point and configuration:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
```

### config.py

Centralized configuration using environment variables:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DATABASE_URL: str
    SECRET_KEY: str

    ALLOWED_ORIGINS: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
```

### database.py

Database connection and session management:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Separation of Concerns

### Models (Database Layer)

```python
# app/models/item.py
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
```

### Schemas (API Layer)

```python
# app/schemas/item.py
from pydantic import BaseModel

class ItemBase(BaseModel):
    title: str
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
```

### CRUD (Data Access Layer)

```python
# app/crud/item.py
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

### Routers (Endpoint Layer)

```python
# app/routers/items.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.item import ItemCreate, ItemResponse
from app.crud import item as crud

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db, item)

@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
```

## Best Practices

1. **Keep routers thin** - Business logic belongs in services or CRUD functions
2. **Use dependency injection** - For database sessions, authentication, etc.
3. **Separate models and schemas** - SQLAlchemy models vs Pydantic schemas
4. **Version your API** - Use `/api/v1/` prefix
5. **Environment-based config** - Use `.env` files and pydantic-settings
6. **Organize by feature** - For large apps, consider feature-based structure
7. **Keep tests alongside code** - Mirror your app structure in tests/

## Environment Files

**.env**
```
PROJECT_NAME="My API"
DATABASE_URL="postgresql://user:pass@localhost/mydb"
SECRET_KEY="your-secret-key"
```

**.env.example** (committed to git)
```
PROJECT_NAME="My API"
DATABASE_URL="postgresql://user:pass@localhost/dbname"
SECRET_KEY="change-this-in-production"
```

## Docker Support

**Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Migration from Small to Large

Start small and refactor as needed:

1. **Start**: Everything in `main.py`
2. **Split**: Move models to `models.py`, schemas to `schemas.py`
3. **Modularize**: Create `routers/` directory for multiple endpoints
4. **Add CRUD**: Separate data access into `crud/` functions
5. **Add services**: Extract business logic to `services/`
6. **Version API**: Move routers to `api/v1/`

Don't over-engineer from the start. Let your structure grow with your needs.
