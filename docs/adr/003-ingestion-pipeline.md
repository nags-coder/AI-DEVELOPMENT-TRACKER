# ADR-003: Ingestion Pipeline

**Status:** Accepted
**Date:** 2025-01-15
**Decision makers:** @nags-coder

## Context

AI Pulse needs to pull content from multiple external platforms, each with different APIs and data formats:

| Source         | API Format     | Content Types        |
|----------------|---------------|----------------------|
| arXiv          | Atom XML      | Papers               |
| GitHub Trending| REST JSON     | Repositories         |
| Hugging Face   | REST JSON     | Models, Spaces, Datasets |

The ingestion system must be:
1. **Pluggable** — Easy to add new sources without modifying existing code
2. **Resilient** — One source failure shouldn't block others
3. **Deduplicating** — Same URL should not create duplicate records
4. **Schedulable** — Run automatically on a cadence and on-demand via API

## Decision

### Registry Pattern

We use a **fetcher registry** to decouple source implementations:

```python
# app/ingestion/registry.py
FETCHER_REGISTRY: dict[str, type[BaseFetcher]] = {
    "arXiv": ArXivFetcher,
    "GitHub Trending": GitHubTrendingFetcher,
    "Hugging Face": HuggingFaceFetcher,
}
```

Each fetcher extends `BaseFetcher`:

```python
class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, source: Source) -> list[dict]:
        """Fetch content items from the external source."""
        ...
```

### Ingestion Runner

The `IngestionRunner` orchestrates the pipeline:

1. Look up the fetcher for the source name in the registry
2. Call `fetcher.fetch(source)` to get raw content dicts
3. For each item, check if `original_url` already exists in `content_items`
4. Insert only new items (upsert-by-URL deduplication)
5. Update `source.last_checked` timestamp

### Celery Integration

```
┌────────────┐     ┌────────────────┐     ┌────────────────┐
│ Celery Beat │────►│ ingest_all()   │────►│ IngestionRunner│
│ (30 min)   │     │ (Celery task)  │     │ .run(source)   │
└────────────┘     └────────────────┘     └──────┬─────────┘
                                                  │
      ┌───────────────────────────────────────────┘
      ▼
┌────────────────┐     ┌────────────────┐     ┌──────────┐
│ ArXivFetcher   │     │ GitHubFetcher  │     │ HFFetcher│
│ (Atom XML)     │     │ (REST API)     │     │ (REST)   │
└────────────────┘     └────────────────┘     └──────────┘
```

- **Celery Beat** schedules `ingest_all_sources` every 30 minutes
- Each source gets its own task for isolation
- Manual trigger available via `POST /api/v1/ingest/trigger`
- After all sources are ingested, `score_all()` re-ranks all items

### Deduplication Strategy

- `content_items.original_url` has a **UNIQUE constraint**
- Before insert, we check for existing URLs in the batch
- Existing items are skipped (not updated) — this keeps user feedback intact
- Future enhancement: update metadata (engagement scores) for existing items

## Alternatives Considered

### Polling with cron
- **Pros:** No Celery dependency
- **Cons:** No retry, no monitoring, can't trigger from API
- **Verdict:** Rejected

### Event-driven with webhooks
- **Pros:** Real-time updates
- **Cons:** Not all sources support webhooks (arXiv doesn't); requires public endpoint
- **Verdict:** Rejected for MVP — may revisit for GitHub webhooks in Phase 3

### ETL framework (Airflow / Prefect)
- **Pros:** Rich DAG management, monitoring UI
- **Cons:** Massive overhead for 3 simple fetchers
- **Verdict:** Rejected — Celery is sufficient at this scale

## Consequences

### Positive
- Adding a new source = one new file implementing `BaseFetcher` + one registry entry
- Source failures are isolated — one broken fetcher doesn't affect others
- URL deduplication prevents data bloat
- Both scheduled and manual triggers supported

### Negative
- Celery adds operational complexity (worker + beat processes)
- No partial update — existing items don't get updated engagement scores (planned for Phase 2)
- Atom XML parsing (arXiv) is more fragile than JSON APIs

## Related
- [ADR-001: System Architecture](001-system-architecture.md)
- [ADR-002: Tech Stack](002-tech-stack.md)
