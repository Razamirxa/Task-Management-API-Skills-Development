# FastAPI Best Practices

Production-ready patterns and recommendations.

## Project Organization

✅ **DO:**
- Use clear directory structure (see project-structure.md)
- Separate models, schemas, and routers
- Use dependency injection for database sessions
- Keep routers thin, move logic to services/CRUD

❌ **DON'T:**
- Put everything in main.py
- Mix business logic with route handlers
- Hardcode configuration values

## Configuration Management

```python
# Use pydantic-settings for configuration
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```

## Error Handling

### Use HTTPException

```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = get_item_from_db(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return item
```

### Custom Exception Handlers

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

app = FastAPI()

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Item {exc.item_id} not found"}
    )
```

## Validation

### Use Pydantic Models

```python
from pydantic import BaseModel, EmailStr, Field, validator

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., gt=0, lt=150)

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v
```

### Response Models

```python
from typing import List

@app.get("/items", response_model=List[ItemResponse])
def list_items():
    return get_all_items()

# Exclude sensitive data
class UserResponse(BaseModel):
    id: int
    email: str
    # password field is excluded

    class Config:
        from_attributes = True
```

## Security

### Environment Variables for Secrets

```python
# Never commit .env file
# Use .env.example as template

# .env
SECRET_KEY="your-secret-key-change-in-production"
DATABASE_URL="postgresql://user:pass@localhost/db"
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourapp.com"],  # Don't use ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/items")
@limiter.limit("5/minute")
async def list_items(request: Request):
    return {"items": []}
```

## Performance

### Use Async Endpoints

```python
# For I/O-bound operations
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user_from_db(db, user_id)
    return user
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email logic
    pass

@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification sent"}
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n: int):
    # Expensive operation
    return result

@app.get("/compute/{n}")
def compute(n: int):
    return expensive_computation(n)
```

## Database

### Use Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Use Indexes

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Index frequently queried fields
    created_at = Column(DateTime, index=True)
```

### Avoid N+1 Queries

```python
# Bad - N+1 queries
users = db.query(User).all()
for user in users:
    user.items  # Triggers separate query for each user

# Good - Eager loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(joinedload(User.items)).all()
```

## Testing

### Separate Test Database

```python
# conftest.py
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)
```

### Test Client

```python
from fastapi.testclient import TestClient

def test_read_item(client: TestClient):
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
```

## Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.get("/items")
def list_items():
    logger.info("Listing all items")
    return get_all_items()
```

## API Versioning

```python
# URL versioning (recommended)
from fastapi import APIRouter

router_v1 = APIRouter(prefix="/api/v1")
router_v2 = APIRouter(prefix="/api/v2")

@router_v1.get("/items")
def list_items_v1():
    return {"version": "v1", "items": []}

@router_v2.get("/items")
def list_items_v2():
    return {"version": "v2", "items": []}

app.include_router(router_v1)
app.include_router(router_v2)
```

## Documentation

### Add Descriptions

```python
@app.get(
    "/items/{item_id}",
    summary="Get an item",
    description="Retrieve an item by its ID",
    response_description="The requested item"
)
def get_item(item_id: int):
    """
    Get an item with all the information:

    - **item_id**: ID of the item
    """
    return {"item_id": item_id}
```

### Customize OpenAPI

```python
app = FastAPI(
    title="My API",
    description="This is my awesome API",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
)
```

## Deployment

### Use Environment Variables

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./default.db")
DEBUG = os.getenv("DEBUG", "False") == "True"
```

### Health Check Endpoint

```python
from sqlalchemy import text

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "detail": str(e)}
```

### Use Production Server

```bash
# Don't use fastapi dev in production
# Use uvicorn with workers

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Best Practices

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Don't run as root
RUN useradd -m appuser
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Common Mistakes to Avoid

1. **Not using async** - Use async/await for I/O operations
2. **Missing indexes** - Index foreign keys and frequently queried fields
3. **No input validation** - Always use Pydantic models
4. **Exposing sensitive data** - Use response models to filter fields
5. **No error handling** - Handle exceptions properly
6. **Hardcoded secrets** - Use environment variables
7. **No rate limiting** - Protect your API from abuse
8. **Sync database calls in async endpoints** - Use async database drivers
9. **Not using dependency injection** - Use FastAPI's Depends()
10. **No tests** - Write tests for critical endpoints

## Performance Checklist

- [ ] Use async endpoints for I/O operations
- [ ] Enable connection pooling
- [ ] Add database indexes
- [ ] Use eager loading to avoid N+1 queries
- [ ] Implement caching for expensive operations
- [ ] Use background tasks for non-urgent operations
- [ ] Enable gzip compression
- [ ] Use CDN for static assets
- [ ] Monitor performance with APM tools

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Validate all inputs with Pydantic
- [ ] Implement authentication and authorization
- [ ] Use environment variables for secrets
- [ ] Configure CORS properly
- [ ] Implement rate limiting
- [ ] Sanitize user inputs
- [ ] Use parameterized queries (SQLAlchemy does this)
- [ ] Keep dependencies updated
- [ ] Enable CSRF protection for state-changing operations

## Production Readiness Checklist

- [ ] Comprehensive error handling
- [ ] Logging configured
- [ ] Health check endpoint
- [ ] Database migrations with Alembic
- [ ] Tests with good coverage
- [ ] API documentation
- [ ] Environment-based configuration
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring and alerting
