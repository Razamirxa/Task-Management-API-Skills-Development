# {{PROJECT_NAME}}

A basic FastAPI application with CRUD operations.

## Features

- ✅ FastAPI with automatic interactive documentation
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Pydantic models for validation
- ✅ Health check endpoint
- ✅ In-memory database (for learning purposes)

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
fastapi dev main.py
```

## API Documentation

Visit http://127.0.0.1:8000/docs for interactive Swagger UI documentation.

Alternative docs: http://127.0.0.1:8000/redoc

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /items` - Create new item
- `GET /items` - List all items
- `GET /items/{item_id}` - Get specific item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

## Example Usage

### Create an item:
```bash
curl -X POST "http://127.0.0.1:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete the tutorial"}'
```

### Get all items:
```bash
curl http://127.0.0.1:8000/items
```

## Next Steps

- Add database integration (see `references/database.md`)
- Implement authentication (see `references/authentication.md`)
- Add tests (see `references/testing.md`)
- Deploy to production (see `references/deployment.md`)

## Project Structure

```
{{PROJECT_NAME}}/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

For production applications, consider using a more structured layout as described in `references/project-structure.md`.
