# System Design — AI Pulse

## 1. Overview

AI Pulse is a personalised AI news aggregator that ingests content from multiple sources (arXiv, GitHub Trending, Hugging Face), scores items by relevance, and surfaces a curated feed through a single-page React application backed by a FastAPI API server.

---

## 2. High-Level Architecture

```
┌───────────────────┐          ┌───────────────────────────────────────────┐
│   React Frontend  │◄────────►│              FastAPI Backend              │
│   Vite + TS + TW  │  proxy   │                                           │
│   :5173           │ /api/*   │  ┌──────────────┐   ┌──────────────────┐  │
└───────────────────┘          │  │  REST API     │   │  Ingestion       │  │
                               │  │  ─ Feed       │   │  Framework       │  │
                               │  │  ─ Sources    │   │  ─ ArXiv         │  │
                               │  │  ─ Content    │   │  ─ GitHub        │  │
                               │  │  ─ Feedback   │   │  ─ HuggingFace   │  │
                               │  └──────┬───────┘   └────────┬─────────┘  │
                               │         │                     │            │
                               │         ▼                     ▼            │
                               │  ┌──────────────────────────────────────┐  │
                               │  │        Scoring Engine (ranker.py)    │  │
                               │  └──────────────┬───────────────────────┘  │
                               │                 │                          │
                               │                 ▼                          │
                               │  ┌──────────────────────────────────────┐  │
                               │  │  PostgreSQL 16  │  Redis 7           │  │
                               │  │  (data store)   │  (Celery broker)   │  │
                               │  └──────────────────────────────────────┘  │
                               └───────────────────────────────────────────┘
                                         ▲                ▲
                                         │                │
                               ┌─────────┴───┐   ┌───────┴─────────┐
                               │ Celery Worker│   │  Celery Beat    │
                               │ (ingestion)  │   │  (every 30 min) │
                               └──────────────┘   └─────────────────┘
```

---

## 3. Component Breakdown

### 3.1 Frontend (React SPA)

| Concern           | Technology                                       |
|-------------------|--------------------------------------------------|
| Framework         | React 19 with TypeScript 5.9                     |
| Build tool        | Vite 8                                           |
| Styling           | Tailwind CSS v4 with shadcn/ui-style components  |
| Data fetching     | TanStack React Query (cache, refetch, mutations) |
| Routing           | React Router v7                                  |
| Icons             | Lucide React                                     |

**Key UI Features:**
- "Must-Read of the Day" hero card
- Paginated feed with infinite-scroll-ready API
- Multi-faceted filter bar (source, type, time range, search)
- Thumbs up/down & bookmark feedback
- Dark mode toggle (system-aware, `localStorage` persistence)
- Auto-refresh every 5 minutes

### 3.2 Backend (FastAPI)

| Layer            | Description                                         |
|------------------|-----------------------------------------------------|
| API routes       | `api/v1/` — Feed, Sources, Content, Ingest, Health  |
| Business logic   | Services layer for CRUD operations                  |
| Ingestion        | Pluggable fetcher framework (registry pattern)       |
| Scoring          | Weighted formula with recency decay                  |
| Task queue       | Celery workers triggered by Beat or API endpoint     |
| Config           | `pydantic-settings` with `.env` file support         |

### 3.3 Database (PostgreSQL 16)

- Async driver: `asyncpg` via SQLAlchemy 2.0 async sessions
- Migrations: Alembic with auto-generated diffs
- Port: **5433** (avoids conflict with local PostgreSQL)
- Tables: `sources`, `sub_sources`, `content_items`, `feedback_log`, `source_change_log`, `filter_presets`

### 3.4 Task Queue (Celery + Redis)

- **Broker & result backend:** Redis 7 at `redis://localhost:6379/0`
- **Celery Beat schedule:** Ingestion runs every 30 minutes
- **Workers:** Process `ingest_source` and `score_all` tasks
- **Trigger:** Automatic (Beat) or manual (POST to `/api/v1/ingest/trigger`)

---

## 4. Data Flow

### 4.1 Ingestion Pipeline

```
External APIs            Celery Worker            Database
─────────────            ─────────────            ────────
arXiv Atom XML  ──►  ┌──────────────┐
GitHub REST API ──►  │ IngestionRunner│ ──► INSERT content_items
HuggingFace API ──►  │ (registry +   │ ──► UPDATE sources.last_checked
                     │  dedup by URL) │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │ score_all()  │ ──► UPDATE content_items.relevance_score
                     └──────────────┘
```

1. **Celery Beat** fires `ingest_all_sources` every 30 minutes.
2. **IngestionRunner** iterates active sources, instantiates the correct fetcher from the registry.
3. Each fetcher returns a list of `ContentItem` dicts.
4. Runner performs **upsert-by-URL** deduplication — existing URLs are skipped.
5. After ingestion completes, `score_all()` re-scores every item.

### 4.2 Feed Request

```
Client                    FastAPI                  Database
──────                    ───────                  ────────
GET /api/v1/feed  ──►  Parse query params  ──►  SELECT content_items
 ?source_id=4          Build SQLAlchemy         JOIN sources
 &type=paper           query with filters       ORDER BY relevance_score DESC
 &time_range=7d        Apply pagination         LIMIT 20 OFFSET 0
 &search=transformer                            ◄── Return rows
                       ◄── Serialize to JSON
◄── JSON response
```

### 4.3 Feedback Loop

```
Client                    FastAPI                  Database
──────                    ───────                  ────────
POST /feedback  ──►  Validate payload  ──►  UPDATE content_items.feedback
 {action: "up"}                            INSERT feedback_log
                    ◄── 200 OK
◄── JSON response
```

---

## 5. Scoring Engine

The relevance score determines feed ordering. Formula:

```
score = 0.4 × recency + 0.3 × quality + 0.2 × engagement + 0.1 × type_boost
```

| Component     | Range   | Calculation                                              |
|---------------|---------|----------------------------------------------------------|
| **recency**   | 0.0–1.0 | Exponential decay: `2^(-age_days / 3.0)`. Zero after 30d |
| **quality**   | 0.0–1.0 | Source `user_rating / 5`. Default 3 if unrated            |
| **engagement**| 0.0–1.0 | `min(engagement_score / 10000, 1.0)`                     |
| **type_boost**| 0.0–1.0 | Content type weight (paper=0.8, repo=0.7, model=0.6 …)  |

**Content Type Weights:**

| Type    | Weight |
|---------|--------|
| paper   | 0.8    |
| repo    | 0.7    |
| model   | 0.6    |
| space   | 0.5    |
| dataset | 0.5    |
| blog    | 0.4    |
| video   | 0.4    |
| news    | 0.3    |

---

## 6. Deployment Topology (Local Development)

| Service       | Container / Process   | Port  |
|---------------|----------------------|-------|
| PostgreSQL 16 | Docker container     | 5433  |
| Redis 7       | Docker container     | 6379  |
| FastAPI       | Local Python process | 8000  |
| Celery Worker | Local Python process | —     |
| Celery Beat   | Local Python process | —     |
| Vite (React)  | Local Node process   | 5173  |

**Docker Compose** manages PostgreSQL and Redis only. Application processes run natively for faster iteration.

---

## 7. Security Considerations (MVP)

- CORS restricted to `http://localhost:5173` (configurable via `CORS_ORIGINS` env var)
- No authentication in MVP — single-user local application
- Database credentials are local dev defaults (not for production)
- GitHub API token optional; stored in `.env` (gitignored)

---

## 8. Future Considerations

- **User accounts** — OAuth2 with JWT tokens
- **ML-based personalisation** — Embedding similarity for content recommendations
- **Horizontal scaling** — Multiple Celery workers, read replicas
- **CDN / static hosting** — Deploy frontend to Vercel/Cloudflare Pages
- **Containerised backend** — Dockerfile for FastAPI + Gunicorn
- **Monitoring** — Prometheus metrics, Sentry error tracking
