# ADR-002: Tech Stack

**Status:** Accepted
**Date:** 2025-01-15
**Decision makers:** @nags-coder

## Context

Selecting the technology stack for AI Pulse. The stack must support:

- Async HTTP handling for fast API responses
- Background task processing
- Rich, interactive single-page frontend
- PostgreSQL with async driver
- Rapid development iteration

## Decision

### Backend

| Choice            | Technology                | Version |
|-------------------|--------------------------|---------|
| Web framework     | **FastAPI**              | 0.135   |
| Validation        | **Pydantic v2**          | 2.x     |
| ORM               | **SQLAlchemy 2.0**       | 2.0.48  |
| Async driver      | **asyncpg**              | latest  |
| Migrations        | **Alembic**              | 1.18    |
| Task queue        | **Celery**               | 5.6     |
| Message broker    | **Redis**                | 7       |
| Database          | **PostgreSQL**           | 16      |
| Settings          | **pydantic-settings**    | latest  |
| Python version    | **3.12**                 | 3.12.x  |

### Frontend

| Choice            | Technology                | Version |
|-------------------|--------------------------|---------|
| UI framework      | **React**                | 19      |
| Build tool        | **Vite**                 | 8       |
| Language          | **TypeScript**           | 5.9     |
| Styling           | **Tailwind CSS**         | v4      |
| Component pattern | **shadcn/ui-style**      | custom  |
| Data fetching     | **TanStack React Query** | 5.x     |
| Routing           | **React Router**         | 7.x     |
| Icons             | **Lucide React**         | latest  |
| Utilities         | **clsx + tailwind-merge**| latest  |

### Testing & Quality

| Choice            | Technology                | Purpose  |
|-------------------|--------------------------|----------|
| Backend tests     | **pytest + pytest-asyncio** | 95 tests |
| HTTP test client  | **httpx**                | Async test requests |
| Backend linting   | **ruff**                 | Fast Python linter |
| Frontend linting  | **ESLint**               | TS/React linting |

## Rationale

### Why FastAPI over Django / Flask?
- **Native async** — First-class `async/await` support for non-blocking DB queries
- **Automatic OpenAPI** — Swagger/ReDoc generated from type hints
- **Pydantic integration** — Request/response validation with zero boilerplate
- **Performance** — One of the fastest Python frameworks

### Why SQLAlchemy 2.0 over Django ORM / Tortoise?
- **Async sessions** — Works natively with `asyncpg`
- **Type annotations** — `Mapped[]` columns with full IDE support
- **Alembic** — Battle-tested migration framework
- **Flexibility** — Not tied to a specific web framework

### Why React over Vue / Svelte?
- **Ecosystem size** — Largest component library and community support
- **TanStack React Query** — Excellent data fetching with cache invalidation
- **TypeScript support** — Best-in-class TS integration
- **Developer familiarity** — Most widely known frontend framework

### Why Vite over Webpack / Next.js?
- **Speed** — Instant HMR, sub-second cold starts
- **Simplicity** — Near-zero config for React + TypeScript
- **No SSR overhead** — SPA-only build is simpler and faster

### Why Tailwind CSS over CSS Modules / Styled Components?
- **Rapid prototyping** — Utility classes for fast UI development
- **Consistency** — Design tokens via config
- **Bundle size** — Purges unused styles automatically
- **shadcn/ui pattern** — Copy-paste components with full customisation

### Why PostgreSQL over SQLite / MySQL?
- **ARRAY columns** — Native `TEXT[]` for topic tags
- **JSONB** — Filter presets stored as JSON
- **GIN indexes** — Efficient array containment queries
- **Production-ready** — Same DB in dev and production

## Consequences

### Positive
- Modern, well-supported stack with excellent documentation
- Strong type safety end-to-end (Pydantic ↔ TypeScript)
- Fast iteration with hot-reload on both frontend and backend
- 95 backend tests provide confidence for refactoring

### Negative
- Python GIL limits CPU-bound parallelism (mitigated by Celery workers)
- Two separate package managers (pip + npm)
- Tailwind class strings can become verbose (mitigated by `cn()` utility)

## Related
- [ADR-001: System Architecture](001-system-architecture.md)
- [ADR-003: Ingestion Pipeline](003-ingestion-pipeline.md)
