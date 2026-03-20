# 🗺️ AI Pulse — Roadmap

> Living document tracking planned phases and features.

---

## Phase 1 — MVP ✅ (Complete)

**Goal:** End-to-end working prototype with multi-source ingestion, scoring, and a polished React feed UI.

**Status:** All 18 steps delivered. Backend has 95 passing tests. Frontend is functional with filters, feedback, dark mode, and auto-refresh.

See [phase-1-mvp.md](phase-1-mvp.md) for the detailed step-by-step breakdown.

### Delivered Capabilities
- Docker infrastructure (PostgreSQL 16, Redis 7)
- FastAPI backend with full REST API (17 endpoints)
- SQLAlchemy 2.0 async models with Alembic migrations
- Ingestion framework with arXiv, GitHub Trending, and Hugging Face fetchers
- Scoring engine (weighted: 0.4 recency + 0.3 quality + 0.2 engagement + 0.1 type)
- Celery task queue with Beat scheduler (30-minute ingestion cycle)
- React 19 + TypeScript + Tailwind CSS frontend
- "Must-Read of the Day" hero card
- Multi-faceted filter bar (source, type, time range, search)
- Thumbs up/down feedback & bookmarks
- Dark mode with system-aware toggle
- Auto-refresh every 5 minutes
- 95 backend tests, ruff-clean, ESLint-clean

---

## Phase 2 — Personalisation & User Accounts 🔲

**Goal:** Multi-user support with persistent preferences and email digests.

### Planned Features
- [ ] User authentication (OAuth2 / magic link)
- [ ] JWT token-based sessions
- [ ] Per-user feed preferences and saved views
- [ ] Email digest — daily or weekly summary of top items
- [ ] Reading history tracking
- [ ] Sub-source ratings affect personalised scoring
- [ ] Export bookmarks to Notion / Obsidian
- [ ] Update existing items with refreshed engagement scores on re-ingest

### Technical Work
- [ ] Add `users` table and auth middleware
- [ ] Migrate feedback & bookmarks to be per-user
- [ ] Add email service integration (SendGrid / Resend)
- [ ] Add `user_preferences` JSONB column

---

## Phase 3 — More Sources & ML Ranking 🔲

**Goal:** Expand content coverage and introduce ML-based personalisation.

### Planned Sources
- [ ] Hacker News (top/best stories)
- [ ] Reddit (r/MachineLearning, r/LocalLLaMA, etc.)
- [ ] Twitter/X (AI researcher accounts)
- [ ] YouTube (AI channels — 3Blue1Brown, Andrej Karpathy, etc.)
- [ ] Blogs (Lilian Weng, Jay Alammar, etc. via RSS)
- [ ] Conference trackers (NeurIPS, ICML, ACL)

### ML Personalisation
- [ ] Embedding-based content similarity (sentence-transformers)
- [ ] User preference vectors from feedback history
- [ ] Hybrid scoring: formula + ML similarity
- [ ] "More like this" recommendations
- [ ] Topic clustering and trend detection

### Technical Work
- [ ] Fetcher plugins for each new source
- [ ] Embedding storage (pgvector extension)
- [ ] Background embedding generation pipeline
- [ ] A/B framework for scoring experiments

---

## Phase 4 — Mobile & Notifications 🔲

**Goal:** Mobile-responsive PWA with push notifications.

### Planned Features
- [ ] Fully responsive mobile layout
- [ ] PWA manifest + service worker (offline support)
- [ ] Push notifications for high-score items
- [ ] Native-feel navigation with swipe gestures
- [ ] Compact card layout for mobile
- [ ] Share to social media / messaging apps

### Technical Work
- [ ] Service worker with workbox
- [ ] Web Push API integration
- [ ] Responsive breakpoints for all components
- [ ] Mobile-specific component variants

---

## Phase 5 — Production & Scale 🔲

**Goal:** Production-ready deployment with monitoring and scaling.

### Planned Features
- [ ] Dockerised backend (FastAPI + Gunicorn)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Frontend deployed to Vercel / Cloudflare Pages
- [ ] Backend deployed to Railway / Fly.io
- [ ] Managed PostgreSQL (Neon / Supabase)
- [ ] Prometheus metrics + Grafana dashboard
- [ ] Sentry error tracking
- [ ] Rate limiting and API keys
- [ ] Health check monitoring (Uptime Kuma)
- [ ] Horizontal Celery worker scaling

---

## Changelog

| Date       | Change                                          |
|------------|------------------------------------------------|
| 2025-01-15 | Phase 1 MVP complete (18 steps, 95 tests)      |
| 2025-01-15 | Roadmap created with Phases 2–5 outlined        |
