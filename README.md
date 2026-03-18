# AI Pulse

> Your personalised AI news aggregator. Surfaces the **one thing you should read today** from arXiv, GitHub Trending, Hugging Face, and more.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for PostgreSQL + Redis)

### 1. Clone & setup environment

```bash
cd ai-pulse
cp .env.example .env
```

### 2. Start infrastructure

```bash
make dev-up          # Starts PostgreSQL + Redis via Docker
```

### 3. Start backend

```bash
make backend-install # Install Python dependencies
make migrate         # Run database migrations
make seed            # Populate initial data
make backend         # Start FastAPI on http://localhost:8000
```

### 4. Start frontend

```bash
make frontend-install  # Install Node dependencies
make frontend          # Start React dev server on http://localhost:5173
```

### 5. Open

- **App:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
ai-pulse/
├── backend/          # FastAPI (Python) — API, ingestion, scoring
├── frontend/         # React (Vite/TS) — UI
├── docs/             # Architecture docs, ADRs
├── plans/            # Phase construction blueprints
├── docker-compose.yml
├── Makefile          # Convenience commands (make help)
└── README.md
```

## Useful Commands

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make dev-up` | Start PostgreSQL + Redis |
| `make backend` | Start FastAPI dev server |
| `make frontend` | Start React dev server |
| `make test` | Run all tests |
| `make lint` | Lint all code |
| `make migrate` | Run database migrations |
| `make seed` | Seed database |
| `make worker` | Start Celery worker |
| `make beat` | Start Celery Beat scheduler |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite) + TypeScript + Tailwind CSS + shadcn/ui |
| Backend | FastAPI (Python 3.12+) + Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Database | PostgreSQL 16 |
| Task Queue | Celery + Redis |
| Testing | pytest (backend) · Vitest + Playwright (frontend) |

## License

Private project.
