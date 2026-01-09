# Task Management API + Skills Development

**AI-400 | Class 1 Project — Panaversity**

A complete Task Management API built using FastAPI, SQLModel, and Neon PostgreSQL, featuring full CRUD operations with comprehensive pytest test coverage.

## 🎬 Demo Video

[![Demo Video](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://github.com/Razamirxa/Task-Management-API-Skills-Development)

## 🚀 Project Overview

This project has three core parts:
1. **Skills Development** - 5 reusable Claude agent skills (3 technical + 2 workflow)
2. **Tech Stack Mastery** - FastAPI, pytest, and SQLModel
3. **Task Management API** - Complete CRUD implementation

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | API Framework |
| **pytest** | Test-Driven Development |
| **SQLModel** | Database Design & Management |
| **Neon PostgreSQL** | Cloud Database |
| **UV** | Python Package Manager |

## 📁 Project Structure

```
├── Task-Management-API/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLModel models
│   ├── test_main.py         # pytest tests (18 tests)
│   ├── pyproject.toml       # Dependencies
│   └── .env.example         # Environment template
│
├── .claude/skills/
│   ├── fastapi/             # FastAPI skill
│   ├── pytest/              # pytest skill
│   ├── sqlmodel/            # SQLModel skill
│   ├── scaffolding-openai-agents/  # AI agent scaffolding
│   └── building-rag-systems/       # RAG system development
│
└── README.md
```

## 🎯 Skills Created (5 Total)

### Technical Skills (3)
| Skill | Purpose |
|-------|---------|
| **fastapi** | API development patterns and best practices |
| **pytest** | Test-driven development with fixtures and mocking |
| **sqlmodel** | Database ORM with Pydantic validation |

### Workflow Skills (2)
| Skill | Purpose |
|-------|---------|
| **scaffolding-openai-agents** | AI agent scaffolding and tool design |
| **building-rag-systems** | RAG system development and chunking strategies |

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tasks/` | Create a new task |
| `GET` | `/tasks/` | Get all tasks |
| `GET` | `/tasks/{id}` | Get a specific task |
| `PUT` | `/tasks/{id}` | Full update a task |
| `PATCH` | `/tasks/{id}` | Partial update a task |
| `DELETE` | `/tasks/{id}` | Delete a task |
| `GET` | `/health` | Health check |

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- UV (Python package manager)
- Neon PostgreSQL account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Razamirxa/Task-Management-API-Skills-Development.git
cd Task-Management-API-Skills-Development/Task-Management-API
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Neon database URL
```

4. Run the server:
```bash
uv run python -m uvicorn main:app --reload
```

5. Open API docs: http://127.0.0.1:8000/docs

### Running Tests

```bash
uv run pytest -v
```

**Result: 18 tests passing ✅**

## 📸 Screenshots

### Swagger UI
Access interactive API documentation at `/docs`

### Test Results
All 18 tests covering CRUD operations pass successfully

## 📚 Additional Skills Reference

| Skill | Purpose |
|-------|---------|
| **browser-use** | Browser automation using Playwright MCP |
| **context7-efficient** | Token-efficient library documentation fetcher |
| **doc-coauthoring** | Structured workflow for co-authoring documentation |
| **docx** | Word document creation, editing, and analysis |
| **pdf** | PDF manipulation toolkit |
| **pptx** | PowerPoint presentation creation and editing |
| **skill-creator** | Guide for creating effective skills |
| **theme-factory** | Styling toolkit with professional themes |
| **xlsx** | Spreadsheet creation and analysis |

## 👨‍💻 Author

**Raza Ul Mustafa**

- GitHub: [@Razamirxa](https://github.com/Razamirxa)

## 📄 License

This project is part of the AI-400: Cloud-Native AI Development course at Panaversity.

---

**Reading Material:** [Claude Code Features and Workflows](https://ai-native.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows)
