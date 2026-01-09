#!/usr/bin/env python3
"""
Generate CRUD Endpoints for a Model

Creates a router file with full CRUD operations for a database model.

Usage:
    python generate_crud.py --model MODEL_NAME [--output-dir DIR]

Examples:
    python generate_crud.py --model Product
    python generate_crud.py --model User --output-dir ./my-project/routers
"""

import argparse
from pathlib import Path


CRUD_ROUTER_TEMPLATE = '''"""
CRUD operations for {{MODEL_NAME}}.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import {{MODEL_NAME}}


router = APIRouter(
    prefix="/{{model_lower}}s",
    tags=["{{model_lower}}s"]
)


# Schemas
class {{MODEL_NAME}}Base(BaseModel):
    """Base schema for {{MODEL_NAME}}"""
    # TODO: Add your model fields here
    # Example:
    # title: str
    # description: str | None = None
    pass


class {{MODEL_NAME}}Create({{MODEL_NAME}}Base):
    """Schema for creating a {{MODEL_NAME}}"""
    pass


class {{MODEL_NAME}}Update({{MODEL_NAME}}Base):
    """Schema for updating a {{MODEL_NAME}}"""
    pass


class {{MODEL_NAME}}Response({{MODEL_NAME}}Base):
    """Schema for {{MODEL_NAME}} response"""
    id: int

    class Config:
        from_attributes = True


# CRUD Operations

@router.post(
    "/",
    response_model={{MODEL_NAME}}Response,
    status_code=status.HTTP_201_CREATED
)
def create_{{model_lower}}(
    {{model_lower}}: {{MODEL_NAME}}Create,
    db: Session = Depends(get_db)
):
    """Create a new {{MODEL_NAME}}."""
    db_{{model_lower}} = {{MODEL_NAME}}(**{{model_lower}}.model_dump())
    db.add(db_{{model_lower}})
    db.commit()
    db.refresh(db_{{model_lower}})
    return db_{{model_lower}}


@router.get("/", response_model=List[{{MODEL_NAME}}Response])
def list_{{model_lower}}s(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all {{MODEL_NAME}}s with pagination."""
    {{model_lower}}s = db.query({{MODEL_NAME}}).offset(skip).limit(limit).all()
    return {{model_lower}}s


@router.get("/{id}", response_model={{MODEL_NAME}}Response)
def get_{{model_lower}}(id: int, db: Session = Depends(get_db)):
    """Get a specific {{MODEL_NAME}} by ID."""
    {{model_lower}} = db.query({{MODEL_NAME}}).filter({{MODEL_NAME}}.id == id).first()

    if not {{model_lower}}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{MODEL_NAME}} not found"
        )

    return {{model_lower}}


@router.put("/{id}", response_model={{MODEL_NAME}}Response)
def update_{{model_lower}}(
    id: int,
    {{model_lower}}_update: {{MODEL_NAME}}Update,
    db: Session = Depends(get_db)
):
    """Update a {{MODEL_NAME}}."""
    db_{{model_lower}} = db.query({{MODEL_NAME}}).filter({{MODEL_NAME}}.id == id).first()

    if not db_{{model_lower}}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{MODEL_NAME}} not found"
        )

    # Update fields
    for key, value in {{model_lower}}_update.model_dump(exclude_unset=True).items():
        setattr(db_{{model_lower}}, key, value)

    db.commit()
    db.refresh(db_{{model_lower}})
    return db_{{model_lower}}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{{model_lower}}(id: int, db: Session = Depends(get_db)):
    """Delete a {{MODEL_NAME}}."""
    db_{{model_lower}} = db.query({{MODEL_NAME}}).filter({{MODEL_NAME}}.id == id).first()

    if not db_{{model_lower}}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{{MODEL_NAME}} not found"
        )

    db.delete(db_{{model_lower}})
    db.commit()
    return None
'''


def generate_crud(model_name: str, output_dir: str):
    """Generate CRUD router for a model."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    model_lower = model_name.lower()

    # Replace placeholders
    content = CRUD_ROUTER_TEMPLATE.replace('{{MODEL_NAME}}', model_name)
    content = content.replace('{{model_lower}}', model_lower)

    # Create router file
    router_file = output_path / f"{model_lower}.py"
    print(f"Creating {router_file}...")
    router_file.write_text(content, encoding='utf-8')

    print(f"\n✅ CRUD router for '{model_name}' created successfully!")
    print(f"\nGenerated file: {router_file}")
    print("\nNext steps:")
    print(f"  1. Update the schema fields in {router_file}")
    print(f"     (Replace the TODO comment with actual fields)")
    print(f"\n  2. Ensure the {model_name} model exists in models.py")
    print(f"\n  3. Include the router in your main.py:")
    print(f"     from .routers.{model_lower} import router as {model_lower}_router")
    print(f"     app.include_router({model_lower}_router)")
    print(f"\n  4. Test the endpoints at http://127.0.0.1:8000/docs")
    print(f"\nAvailable endpoints:")
    print(f"  POST   /{model_lower}s/     - Create a new {model_name}")
    print(f"  GET    /{model_lower}s/     - List all {model_name}s")
    print(f"  GET    /{model_lower}s/{{id}} - Get a specific {model_name}")
    print(f"  PUT    /{model_lower}s/{{id}} - Update a {model_name}")
    print(f"  DELETE /{model_lower}s/{{id}} - Delete a {model_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate CRUD endpoints for a FastAPI model"
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Model name (e.g., Product, User, Article)"
    )

    parser.add_argument(
        "--output-dir",
        default="./routers",
        help="Output directory for router file (default: ./routers)"
    )

    args = parser.parse_args()
    generate_crud(args.model, args.output_dir)


if __name__ == "__main__":
    main()
