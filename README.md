# ⚡ AI Pulse

**Your personalised AI news aggregator.** Cuts through the noise across arXiv, GitHub Trending, and Hugging Face to surface the **one thing you should read today**.

![AI Pulse Screenshot](docs/screenshot.png)

---

## ✨ Features

- **"Must-Read" of the Day** — A single top-scored item surfaced from all sources so you never miss what matters.
- **Multi-Source Ingestion** — Pulls papers, repos, models, and Spaces from arXiv, GitHub, and Hugging Face.
- **Smart Scoring Engine** — Ranks content using recency decay, quality signals, engagement metrics, and content-type boosts.
- **Powerful Filters** — Search, filter by time range (today / 7d / 30d), content type (paper / repo / model / space), and source.
- **Feedback Loop** — Thumbs up/down and bookmarks to personalise your feed over time.
- **Dark Mode** — System-aware theme toggle with `localStorage` persistence.
- **Auto-Refresh** — Feed refreshes every 5 minutes; manual refresh button in the header.
- **Scheduled Ingestion** — Celery Beat runs ingestion every 30 minutes to keep content fresh.

---

## 🏗️ Architecture

```
┌──────────────┐        ┌──────────────────────────────────────┐
│   React UI   │◄──────►│           FastAPI Backend            │
│  (Vite + TS) │  proxy │                                      │
│  :5173       │ /api/* │  ┌─────────┐  ┌────────┐  ┌───────┐ │
└──────────────┘        │  │ Feed API│  │Ingest  │  │Score  │ │
                        │  │ Sources │  │Framework│  │Engine │ │
                        │  │ Content │  │ ArXiv   │  │Ranker │ │
                        │  │ Feedback│  │ GitHub  │  │       │ │
                        │  └────┬────┘  │ HF      │  └───┬───┘ │
                        │       │       └────┬─────┘     │     │
                        │       ▼            ▼           ▼     │
                        │  ┌─────────────────────────────────┐ │
                        │  │  PostgreSQL 16  │  Redis 7      │ │
                        │  │  (data store)   │  (cache/queue)│ │
                        │  └─────────────────────────────────┘ │
                        └──────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 20+ | Frontend tooling |
| Docker | 20+ | PostgreSQL + Redis |

### 1. Clone & configure

```bash
git clone <your-repo-url> ai-pulse
cd ai-pulse
cp .env.example .env        # Defaults work for local dev
```

### 2. Start infrastructure

```bash
make dev-up                  # PostgreSQL (port 5433) + Redis (port 6379)
```

### 3. Start backend

```bash
make backend-install         # pip install -e ".[dev]"
make migrate                 # Alembic → head
make seed                    # Populate sample data
make backend                 # FastAPI on http://localhost:8000
```

### 4. Start frontend

```bash
make frontend-install        # npm install
make frontend                # Vite on http://localhost:5173
```

### 5. Open

| URL | What |
|-----|------|
| http://localhost:5173 | **App** — Main UI |
| http://localhost:8000/docs | **Swagger** — Interactive API docs |
| http://localhost:8000/redoc | **ReDoc** — Alternative API docs |

---

## 📁 Project Structure

```
ai-pulse/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (feed, sources, content, ingest, health)
│   │   ├── ingestion/       # Source fetchers (arXiv, GitHub, HuggingFace)
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── scoring/         # Relevance ranking engine
│   │   ├── services/        # Business logic layer
│   │   ├── tasks/           # Celery tasks & beat schedule
│   │   ├── config.py        # Pydantic Settings
│   │   ├── database.py      # Async engine & session
│   │   └── main.py          # FastAPI app entrypoint
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Seed data & utilities
│   ├── tests/               # pytest test suite (95 tests)
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/      # UI components (FeedCard, Header, Filters, etc.)
│   │   ├── hooks/           # React Query hooks (useFeed, useMustRead, etc.)
│   │   ├── lib/             # Utilities (api client, cn, formatDate)
│   │   ├── types/           # TypeScript type definitions
│   │   ├── App.tsx          # Main app layout
│   │   └── main.tsx         # Entry point with providers
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
├── docs/                    # Architecture docs & ADRs
├── plans/                   # Phase construction blueprints
├── docker-compose.yml       # PostgreSQL 16 + Redis 7
├── Makefile                 # All dev commands (make help)
├── .env.example             # Environment template
└── .gitignore
```

---

## 🔌 API Endpoints

All routes are prefixed with `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (DB + Redis) |
| `GET` | `/feed` | Paginated feed with filters (source, type, time, search, sort) |
| `GET` | `/feed/must-read` | Today's single highest-scored item |
| `GET` | `/sources` | List all sources |
| `POST` | `/sources` | Create a new source |
| `PUT` | `/sources/:id` | Update a source |
| `DELETE` | `/sources/:id` | Soft-delete a source |
| `GET` | `/sub-sources` | List sub-sources |
| `POST` | `/sub-sources` | Create a sub-source |
| `PATCH` | `/sub-sources/:id/rate` | Rate a sub-source |
| `GET` | `/content/:id` | Get content item detail |
| `POST` | `/content/:id/feedback` | Submit thumbs up/down |
| `POST` | `/content/:id/save` | Bookmark an item |
| `DELETE` | `/content/:id/save` | Remove bookmark |
| `POST` | `/ingest/trigger` | Trigger ingestion for all sources |
| `POST` | `/ingest/trigger/:source_id` | Trigger ingestion for one source |
| `POST` | `/ingest/score` | Re-score all content items |

---

## ⚙️ Environment Variables

Defined in `.env` (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://aipulse:localdev@localhost:5433/aipulse` | Async PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for Celery broker + cache |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins (comma-separated) |
| `LOG_LEVEL` | `info` | Logging level |
| `API_V1_PREFIX` | `/api/v1` | API route prefix |
| `GITHUB_TOKEN` | *(empty)* | GitHub API token (optional, raises rate limit) |

> **Note:** PostgreSQL runs on port **5433** (not 5432) to avoid conflicts with local installations.

---

## 🧪 Development

### Run tests

```bash
make test              # All tests (backend + frontend)
make test-backend      # Backend only (95 pytest tests)
make test-frontend     # Frontend only
```

### Lint & format

```bash
make lint              # Check (ruff + eslint)
make lint-fix          # Auto-fix
```

### Database

```bash
make migrate           # Apply migrations
make migrate-new msg="add_users"  # Generate new migration
make migrate-down      # Rollback one step
make seed              # Re-seed sample data
make dev-reset         # Nuke DB volumes & start fresh
```

### Background workers

```bash
make worker            # Celery worker (processes ingestion tasks)
make beat              # Celery Beat (schedules ingestion every 30 min)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 · Vite 8 · TypeScript 5.9 · Tailwind CSS v4 · shadcn/ui-style components |
| **State** | TanStack React Query · React Router |
| **Backend** | FastAPI · Pydantic v2 · Python 3.12 |
| **ORM** | SQLAlchemy 2.0 (async + asyncpg) · Alembic |
| **Database** | PostgreSQL 16 |
| **Task Queue** | Celery 5.6 · Redis 7 |
| **Ingestion** | arXiv Atom XML · GitHub Search API · Hugging Face API |
| **Scoring** | Weighted formula: 0.4 recency + 0.3 quality + 0.2 engagement + 0.1 type boost |
| **Testing** | pytest · pytest-asyncio · httpx (95 backend tests) |
| **Linting** | ruff (backend) · ESLint (frontend) |

---

## 📋 Makefile Reference

Run `make help` to see all commands, or reference below:

| Command | Description |
|---------|-------------|
| `make dev-up` | Start PostgreSQL + Redis containers |
| `make dev-down` | Stop containers |
| `make dev-reset` | Stop + delete volumes (fresh DB) |
| `make backend` | Start FastAPI dev server (port 8000) |
| `make backend-install` | Install Python dependencies |
| `make frontend` | Start Vite dev server (port 5173) |
| `make frontend-install` | Install Node dependencies |
| `make test` | Run all tests |
| `make test-backend` | Run backend tests only |
| `make test-frontend` | Run frontend tests only |
| `make lint` | Lint all code |
| `make lint-fix` | Auto-fix lint issues |
| `make migrate` | Apply database migrations |
| `make migrate-new msg="..."` | Generate a new migration |
| `make migrate-down` | Rollback one migration |
| `make seed` | Seed database with sample data |
| `make worker` | Start Celery worker |
| `make beat` | Start Celery Beat scheduler |
| `make clean` | Remove build artifacts & caches |

---

## 🗺️ Roadmap

See [plans/ROADMAP.md](plans/ROADMAP.md) for the full roadmap. Current status:

- [x] **Phase 1 — MVP** (Steps 1–18): Backend, API, ingestion, scoring, frontend, end-to-end
- [ ] **Phase 2** — User accounts, saved views, email digest
- [ ] **Phase 3** — ML-based personalisation, more sources (Twitter/X, Reddit, Hacker News)
- [ ] **Phase 4** — Mobile-responsive PWA, push notifications

---

## 📄 License

Private project — not open-source at this time.
