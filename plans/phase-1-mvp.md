# Phase 1 — MVP Construction Plan

**Status:** ✅ Complete
**Duration:** Initial build
**Tests:** 95 passing (backend)

---

## Steps Overview

| Step | Title                          | Status |
|------|--------------------------------|--------|
| 1    | Docker Infrastructure          | ✅     |
| 2    | FastAPI Scaffold               | ✅     |
| 3    | Database Models                | ✅     |
| 4    | Seed Data                      | ✅     |
| 5    | Feed API                       | ✅     |
| 6    | Source & Content CRUD          | ✅     |
| 7    | Ingestion Framework            | ✅     |
| 8    | arXiv Fetcher                  | ✅     |
| 9    | GitHub Trending Fetcher        | ✅     |
| 10   | Hugging Face Fetcher           | ✅     |
| 11   | Scoring Engine                 | ✅     |
| 12   | Frontend Scaffold              | ✅     |
| 13   | UI Shell & Components          | ✅     |
| 14   | API Wiring (React Query)       | ✅     |
| 15   | Filter Bar                     | ✅     |
| 16   | Feedback & Bookmarks           | ✅     |
| 17   | Auto-Refresh & Polish          | ✅     |
| 18   | Testing & Quality              | ✅     |

---

## Step Details

### Step 1: Docker Infrastructure
- Created `docker-compose.yml` with PostgreSQL 16-alpine and Redis 7-alpine
- PostgreSQL on port **5433** (avoids conflicts with local installs)
- Redis on port 6379
- Named volumes for data persistence
- Health checks for both services

### Step 2: FastAPI Scaffold
- Initialised `backend/` with `pyproject.toml` (editable install)
- Created `app/main.py` with FastAPI application
- Configured CORS middleware
- Set up `pydantic-settings` for environment configuration
- Created `.env.example` template
- Built `Makefile` with all dev commands

### Step 3: Database Models
- Set up SQLAlchemy 2.0 with `DeclarativeBase` and `Mapped[]` annotations
- Created 6 models: `Source`, `SubSource`, `ContentItem`, `FeedbackLog`, `SourceChangeLog`, `FilterPreset`
- Configured async engine with `asyncpg`
- Set up Alembic for migrations with async support
- Added indexes for performance (GIN index on topic_tags)

### Step 4: Seed Data
- Created `scripts/seed.py` with sample data
- 3 sources: arXiv, GitHub Trending, Hugging Face
- 15 content items with real URLs and metadata
- Idempotent — safe to run multiple times

### Step 5: Feed API
- `GET /api/v1/feed` — Paginated feed with filters
- `GET /api/v1/feed/must-read` — Highest-scored item today
- Query params: `source_id`, `type`, `time_range`, `search`, `sort`, `page`, `size`
- Full-text search on title and summary
- Time range filters: `today`, `7d`, `30d`
- Sort options: `score`, `date`, `engagement`

### Step 6: Source & Content CRUD
- Full CRUD for sources (create, read, update, soft-delete)
- Sub-source management with rating endpoint
- Content detail, feedback, and bookmark endpoints
- Audit logging via `SourceChangeLog`

### Step 7: Ingestion Framework
- `BaseFetcher` abstract class with `fetch()` method
- `FETCHER_REGISTRY` mapping source names to fetcher classes
- `IngestionRunner` orchestrates fetch → dedup → insert pipeline
- URL-based deduplication (UNIQUE constraint on `original_url`)

### Step 8: arXiv Fetcher
- Parses Atom XML from arXiv API
- Extracts: title, authors, abstract, published date, categories
- Maps categories to topic tags
- Handles pagination and rate limiting

### Step 9: GitHub Trending Fetcher
- Uses GitHub Search API (`/search/repositories`)
- Sorts by stars in recent timeframe
- Extracts: repo name, description, stars, language, topics
- Respects rate limits (optional `GITHUB_TOKEN` for higher limits)

### Step 10: Hugging Face Fetcher
- Fetches from Hugging Face Hub API
- Supports models, datasets, and Spaces
- Extracts: model name, author, downloads, likes, tags
- Maps pipeline tags to content topics

### Step 11: Scoring Engine
- Weighted formula: `0.4×recency + 0.3×quality + 0.2×engagement + 0.1×type_boost`
- Recency: exponential decay with 3-day half-life
- Quality: source user_rating normalised to 0–1
- Engagement: capped at 10,000 (stars/downloads)
- Type boost: paper=0.8, repo=0.7, model=0.6, space=0.5, etc.
- `score_all()` re-scores entire database

### Step 12: Frontend Scaffold
- Vite + React 19 + TypeScript 5.9
- Tailwind CSS v4 configuration
- shadcn/ui-style component system (`cn()` utility)
- React Router for routing
- TanStack React Query provider

### Step 13: UI Shell & Components
- `Header` with logo, dark mode toggle, refresh button
- `FeedCard` with source badge, type icon, score bar, action buttons
- `MustReadCard` hero component for top item
- `FilterBar` with dropdowns and search input
- Dark mode with `localStorage` persistence and system detection

### Step 14: API Wiring
- Custom hooks: `useFeed`, `useMustRead`, `useSources`
- React Query for caching, background refetch, and optimistic updates
- API client with base URL and error handling
- Type definitions matching backend schemas

### Step 15: Filter Bar
- Source filter dropdown (populated from API)
- Content type filter (paper, repo, model, space)
- Time range filter (today, 7 days, 30 days)
- Search input with debounce
- URL query params sync for shareable filter state

### Step 16: Feedback & Bookmarks
- Thumbs up/down buttons on each card
- Bookmark toggle with optimistic UI update
- `useFeedback` and `useBookmark` mutation hooks
- Visual state feedback (filled icons for active state)

### Step 17: Auto-Refresh & Polish
- Auto-refresh every 5 minutes via React Query `refetchInterval`
- Manual refresh button in header
- Loading skeletons during data fetch
- Error states with retry button
- Empty states for no results

### Step 18: Testing & Quality
- 95 backend tests covering all API endpoints
- Async test fixtures with in-memory database
- ruff linting (zero violations)
- ESLint (zero violations)
- TypeScript strict mode (zero errors)
- Production build verification

---

## Git History

| Commit   | Scope                                     |
|----------|-------------------------------------------|
| `202ef5c`| Steps 1–4: Docker, FastAPI, models, seed  |
| `1854c1e`| Step 5: Feed API + pagination             |
| `b6a425f`| Step 6: Source & Content CRUD             |
| `60f1fce`| Step 7: Ingestion framework + Celery      |
| `1e2e723`| Steps 8–10: ArXiv, GitHub, HF fetchers   |
| `ca1ae13`| Step 11: Scoring engine                   |
| `f118c75`| Steps 12–13: Frontend scaffold + UI shell |
| `5f75d0e`| Steps 14–17: Wiring, filters, feedback    |
| `87695e8`| Chore: README, seed URLs, .gitignore      |
