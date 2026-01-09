#!/usr/bin/env python3
"""
FastAPI Project Scaffolding Script

Generates a new FastAPI project from predefined templates.

Usage:
    python scaffold_project.py <project-name> --template <template-type>

Examples:
    python scaffold_project.py my-api
    python scaffold_project.py my-api --template rest-api
    python scaffold_project.py my-service --template microservice
"""

import argparse
import os
import shutil
import sys
from pathlib import Path


TEMPLATES = {
    "hello-world": "Basic FastAPI application",
    "rest-api": "REST API with database integration",
    "auth-api": "API with JWT authentication",
    "full-stack": "FastAPI backend + frontend integration",
    "microservice": "Microservice architecture"
}


def get_skill_dir():
    """Get the skill directory path."""
    # This script is in skills/fastapi/scripts/, so go up 1 level
    return Path(__file__).parent.parent


def get_template_dir(template_name):
    """Get the template directory path."""
    skill_dir = get_skill_dir()
    template_dir = skill_dir / "assets" / "templates" / template_name

    if not template_dir.exists():
        print(f"Error: Template '{template_name}' not found at {template_dir}")
        sys.exit(1)

    return template_dir


def scaffold_project(project_name, template_name, output_dir):
    """Create a new FastAPI project from template."""

    # Get template directory
    template_dir = get_template_dir(template_name)

    # Create output directory
    project_path = Path(output_dir) / project_name

    if project_path.exists():
        response = input(f"Directory '{project_path}' already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
        shutil.rmtree(project_path)

    # Copy template
    print(f"Creating project '{project_name}' from template '{template_name}'...")
    shutil.copytree(template_dir, project_path)

    # Replace placeholders in files
    replace_placeholders(project_path, project_name)

    print(f"\n✅ Project created successfully at: {project_path}")
    print(f"\nNext steps:")
    print(f"  1. cd {project_name}")
    print(f"  2. python -m venv venv")
    print(f"  3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print(f"  4. pip install -r requirements.txt")
    print(f"  5. fastapi dev main.py")
    print(f"\nVisit http://127.0.0.1:8000/docs for interactive API documentation")


def replace_placeholders(project_path, project_name):
    """Replace {{PROJECT_NAME}} placeholders in all files."""

    for root, dirs, files in os.walk(project_path):
        # Skip __pycache__ and .git directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'venv', '.venv']]

        for file in files:
            file_path = Path(root) / file

            # Skip binary files
            if file_path.suffix in ['.pyc', '.pyo', '.so', '.dll', '.dylib']:
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                if '{{PROJECT_NAME}}' in content:
                    content = content.replace('{{PROJECT_NAME}}', project_name)
                    file_path.write_text(content, encoding='utf-8')
            except (UnicodeDecodeError, PermissionError):
                # Skip binary or protected files
                pass


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new FastAPI project from template",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "project_name",
        help="Name of the project to create"
    )

    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        default="hello-world",
        help="Template to use (default: hello-world)"
    )

    parser.add_argument(
        "--output",
        default=".",
        help="Output directory (default: current directory)"
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates"
    )

    args = parser.parse_args()

    if args.list_templates:
        print("Available templates:")
        for name, description in TEMPLATES.items():
            print(f"  {name:15} - {description}")
        sys.exit(0)

    scaffold_project(args.project_name, args.template, args.output)


if __name__ == "__main__":
    main()
