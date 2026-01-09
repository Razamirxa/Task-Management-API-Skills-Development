"""
{{PROJECT_NAME}} - Basic FastAPI Application

A minimal FastAPI application to get you started.

Run with: fastapi dev main.py
Visit: http://127.0.0.1:8000/docs for interactive API documentation
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="{{PROJECT_NAME}}",
    description="A basic FastAPI application",
    version="1.0.0"
)

# In-memory database (for demonstration)
items_db = []


# Pydantic models
class Item(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    completed: bool = False


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


# Routes

@app.get("/")
def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to {{PROJECT_NAME}}!",
        "docs": "/docs",
        "endpoints": {
            "create_item": "POST /items",
            "list_items": "GET /items",
            "get_item": "GET /items/{item_id}",
            "update_item": "PUT /items/{item_id}",
            "delete_item": "DELETE /items/{item_id}"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    """Create a new item"""
    new_item = Item(
        id=len(items_db) + 1,
        title=item.title,
        description=item.description
    )
    items_db.append(new_item)
    return new_item


@app.get("/items", response_model=List[Item])
def list_items(skip: int = 0, limit: int = 10):
    """List all items with pagination"""
    return items_db[skip: skip + limit]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    """Get a specific item by ID"""
    for item in items_db:
        if item.id == item_id:
            return item

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item_update: ItemCreate):
    """Update an existing item"""
    for item in items_db:
        if item.id == item_id:
            item.title = item_update.title
            item.description = item_update.description
            return item

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    """Delete an item"""
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return

    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
