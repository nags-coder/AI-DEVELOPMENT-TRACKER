# ADR-001: System Architecture

**Status:** Accepted
**Date:** 2025-01-15
**Decision makers:** @nags-coder

## Context

We need an architecture for AI Pulse — a personalised AI news aggregator that pulls content from multiple platforms (arXiv, GitHub, Hugging Face), ranks items by relevance, and presents them in a curated feed. The system must:

1. Ingest content from heterogeneous sources (REST APIs, Atom XML feeds)
2. Score and rank items using a weighted formula
3. Serve a responsive single-page application
4. Support background processing for ingestion
5. Be simple enough for a solo developer to build and maintain

## Decision

We adopt a **modular monolith** architecture with clear internal boundaries:

```
┌─────────────────────────────────────────────┐
│              FastAPI Application             │
│  ┌──────────┬──────────┬──────────────────┐ │
│  │ REST API │ Ingest.  │ Scoring Engine   │ │
│  │ Layer    │ Framework│                  │ │
│  └────┬─────┴────┬─────┴────────┬─────────┘ │
│       └──────────┴──────────────┘            │
│              SQLAlchemy ORM                  │
│              PostgreSQL 16                   │
└─────────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    React SPA            Celery Workers
    (separate build)     (same codebase)
```

### Key architectural decisions:

1. **Single backend codebase** — API routes, ingestion, and scoring live in the same Python package (`app/`), sharing models and database sessions.

2. **Separate frontend build** — React SPA built with Vite, communicates via REST API. No server-side rendering. Vite proxies `/api/*` to FastAPI in dev.

3. **Background tasks via Celery** — Ingestion runs as Celery tasks dispatched by Beat (scheduled) or API (manual). Workers share the same codebase but run as separate processes.

4. **PostgreSQL as single source of truth** — All state lives in PostgreSQL. Redis is used only as a Celery broker, not as a primary data store.

5. **No microservices** — At MVP scale, a modular monolith is simpler to develop, test, and deploy. Service boundaries are enforced by Python package structure, not network calls.

## Alternatives Considered

### Microservices
- **Pros:** Independent scaling, technology diversity
- **Cons:** Operational overhead (service discovery, distributed tracing, network failures) far exceeds MVP needs
- **Verdict:** Rejected — premature for a single-user tool

### Server-side rendering (Next.js)
- **Pros:** Better SEO, simpler data fetching
- **Cons:** Couples frontend to Node.js runtime, more complex deployment
- **Verdict:** Rejected — SEO not needed for a personal tool; SPA is simpler

### Cron jobs instead of Celery
- **Pros:** Zero additional infrastructure
- **Cons:** No task retry, no result tracking, no API-triggered ingestion
- **Verdict:** Rejected — Celery provides better observability and control

## Consequences

### Positive
- Fast development velocity — one language for the entire backend
- Easy testing — models, services, and API handlers all in one pytest suite
- Simple deployment — two processes (API + worker) plus Docker for infrastructure
- Clean separation — frontend is a static build that can be deployed independently

### Negative
- Scaling requires splitting into services if user count grows significantly
- Celery adds Redis as an infrastructure dependency
- No server-side rendering means no SEO (acceptable for a personal tool)

## Related
- [ADR-002: Tech Stack](002-tech-stack.md)
- [ADR-003: Ingestion Pipeline](003-ingestion-pipeline.md)
