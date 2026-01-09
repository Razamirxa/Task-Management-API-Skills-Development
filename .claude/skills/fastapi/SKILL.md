---
name: fastapi
description: Comprehensive FastAPI development skill for building Python web APIs from hello world to production-ready applications. Use when building REST APIs, implementing authentication, integrating databases, adding WebSockets, creating microservices, or any FastAPI development task. Covers project scaffolding, CRUD operations, testing, deployment, and best practices.
---

# FastAPI Development Skill

Build professional FastAPI applications from beginner to advanced level.

## Quick Start

### Create New Project

Use the scaffolding script to generate a new FastAPI project:

```bash
python scripts/scaffold_project.py <project-name> --template <template-type>
```

**Template types:**
- `hello-world` - Minimal FastAPI app (default)
- `rest-api` - REST API with database integration
- `auth-api` - API with JWT authentication
- `full-stack` - FastAPI backend + frontend integration
- `microservice` - Microservice architecture

### Add Features to Existing Project

```bash
# Add authentication
python scripts/add_auth.py

# Add database support
python scripts/add_database.py --db-type postgresql

# Generate CRUD endpoints for a model
python scripts/generate_crud.py --model User
```

## Project Templates

Ready-made templates are available in `assets/templates/`:

- **hello-world/** - Basic FastAPI application
- **rest-api/** - REST API with SQLAlchemy database
- **auth-api/** - Complete authentication system
- **full-stack/** - Backend + frontend integration
- **microservice/** - Microservice with Docker

Each template includes:
- Proper project structure
- Configuration management
- Testing setup
- Documentation
- Docker files

## Reference Documentation

Comprehensive guides are available in `references/`:

- **[project-structure.md](references/project-structure.md)** - Organizing FastAPI projects
- **[database.md](references/database.md)** - Database integration (SQLAlchemy, async)
- **[authentication.md](references/authentication.md)** - JWT, OAuth2 patterns
- **[crud-patterns.md](references/crud-patterns.md)** - CRUD operation best practices
- **[testing.md](references/testing.md)** - Testing strategies
- **[deployment.md](references/deployment.md)** - Deployment guides (Docker, cloud)
- **[websockets.md](references/websockets.md)** - WebSocket implementation
- **[background-tasks.md](references/background-tasks.md)** - Async job patterns
- **[middleware.md](references/middleware.md)** - Custom middleware
- **[best-practices.md](references/best-practices.md)** - Performance, security, production tips
- **[api-design.md](references/api-design.md)** - RESTful API design patterns

## Common Workflows

### Workflow 1: Create a New API from Scratch

1. Scaffold the project:
   ```bash
   python scripts/scaffold_project.py my-api --template rest-api
   ```

2. Review the generated structure in `references/project-structure.md`

3. Define your models and generate CRUD:
   ```bash
   python scripts/generate_crud.py --model Product
   ```

4. Add authentication if needed:
   ```bash
   python scripts/add_auth.py
   ```

5. Write tests following patterns in `references/testing.md`

6. Deploy using guides in `references/deployment.md`

### Workflow 2: Add Database to Existing Project

1. Run the database setup script:
   ```bash
   python scripts/add_database.py --db-type postgresql
   ```

2. Review database patterns in `references/database.md`

3. Define models using SQLAlchemy

4. Generate CRUD endpoints:
   ```bash
   python scripts/generate_crud.py --model YourModel
   ```

### Workflow 3: Implement Authentication

1. Add authentication scaffolding:
   ```bash
   python scripts/add_auth.py
   ```

2. Review authentication patterns in `references/authentication.md`

3. Customize JWT settings and user model

4. Implement protected endpoints

### Workflow 4: Build a Microservice

1. Create from microservice template:
   ```bash
   python scripts/scaffold_project.py my-service --template microservice
   ```

2. Review the generated Docker and docker-compose files

3. Implement service-specific endpoints

4. Deploy using containerization

## Development Tips

### When Starting a New Feature

1. Check if a template exists in `assets/templates/`
2. Review relevant documentation in `references/`
3. Use scaffolding scripts to generate boilerplate
4. Follow patterns from the references

### When Stuck

1. **Project structure questions** → See `references/project-structure.md`
2. **Database issues** → See `references/database.md`
3. **Auth problems** → See `references/authentication.md`
4. **Performance concerns** → See `references/best-practices.md`
5. **Testing questions** → See `references/testing.md`
6. **Deployment issues** → See `references/deployment.md`

### Best Practices

Always refer to `references/best-practices.md` for:
- Performance optimization
- Security considerations
- Production deployment
- Error handling
- Logging strategies
- API versioning

## Progressive Learning Path

**Beginner (Hello World → Basic API)**
1. Start with `assets/templates/hello-world/`
2. Read `references/project-structure.md`
3. Build simple endpoints with path/query parameters

**Intermediate (Database Integration)**
1. Use `assets/templates/rest-api/`
2. Read `references/database.md`
3. Implement CRUD operations
4. Add validation with Pydantic

**Advanced (Authentication & Production)**
1. Use `assets/templates/auth-api/`
2. Read `references/authentication.md`
3. Implement JWT auth
4. Add middleware and background tasks
5. Write comprehensive tests

**Professional (Microservices & Deployment)**
1. Use `assets/templates/microservice/`
2. Read `references/deployment.md`
3. Containerize with Docker
4. Set up CI/CD
5. Deploy to cloud platforms

## Scripts Reference

All scripts in `scripts/` are designed to be run from the project root:

- **scaffold_project.py** - Generate new FastAPI project from template
- **add_auth.py** - Add JWT authentication to existing project
- **add_database.py** - Set up database configuration and models
- **generate_crud.py** - Generate CRUD endpoints for a model
- **add_tests.py** - Add test files for a module

Run any script with `--help` for detailed usage information.
