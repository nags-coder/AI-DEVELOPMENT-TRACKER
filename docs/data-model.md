# Data Model — AI Pulse

## Overview

AI Pulse uses PostgreSQL 16 with SQLAlchemy 2.0 (async mode via `asyncpg`). All models inherit from a shared `DeclarativeBase` and use SQLAlchemy's `Mapped[]` type annotations.

---

## Entity-Relationship Diagram

```
┌────────────────────┐       ┌────────────────────────┐
│     sources         │       │     sub_sources         │
├────────────────────┤       ├────────────────────────┤
│ id (PK)            │───┐   │ id (PK)                │
│ name (unique)      │   │   │ source_id (FK→sources) │◄──┐
│ category           │   │   │ platform               │   │
│ base_url           │   ├──►│ handle                 │   │
│ source_type        │   │   │ display_name           │   │
│ priority (1–5)     │   │   │ user_rating (1–5)      │   │
│ status             │   │   │ status                 │   │
│ user_rating (1–5)  │   │   │ last_fetched           │   │
│ quality_score      │   │   │ content_count          │   │
│ added_at           │   │   │ avg_quality            │   │
│ last_checked       │   │   │ added_at               │   │
│ notes              │   │   └────────────────────────┘   │
└────────────────────┘   │                                 │
        │                │   ┌────────────────────────────┐│
        │                │   │     content_items           ││
        │                │   ├────────────────────────────┤│
        │                │   │ id (PK)                    ││
        │                ├──►│ source_id (FK→sources)     ││
        │                    │ sub_source_id (FK→sub_src) │┘
        │                    │ title                      │
        │                    │ summary                    │
        │                    │ original_url (unique)      │
        │                    │ author                     │
        │                    │ published_at               │
        │                    │ fetched_at                 │
        │                    │ content_type               │
        │                    │ thumbnail_url              │
        │                    │ topic_tags (TEXT[])         │
        │                    │ relevance_score            │
        │                    │ engagement_score           │
        │                    │ is_read                    │
        │                    │ is_saved                   │
        │                    │ feedback (up/down/null)    │
        │                    └────────────┬───────────────┘
        │                                 │
        │   ┌───────────────────────┐     │
        │   │   source_change_log    │     │   ┌────────────────────┐
        │   ├───────────────────────┤     │   │   feedback_log      │
        │   │ id (PK)               │     │   ├────────────────────┤
        └──►│ source_id (FK→sources)│     │   │ id (PK)            │
            │ field_changed         │     └──►│ content_id (FK)    │
            │ old_value             │         │ action (up/down)   │
            │ new_value             │         │ created_at         │
            │ reason                │         └────────────────────┘
            │ changed_at            │
            └───────────────────────┘

┌────────────────────────┐
│    filter_presets        │
├────────────────────────┤
│ id (PK)                │
│ name                   │
│ filters_json (JSONB)   │
│ is_default             │
│ created_at             │
└────────────────────────┘
```

---

## Table Definitions

### `sources`

Top-level content platforms (e.g., arXiv, GitHub Trending, Hugging Face).

| Column         | Type           | Constraints              | Description                        |
|----------------|----------------|--------------------------|------------------------------------|
| `id`           | `INTEGER`      | PK, auto-increment       | Unique source identifier           |
| `name`         | `VARCHAR(100)` | UNIQUE, NOT NULL          | Human-readable name                |
| `category`     | `VARCHAR(50)`  | NOT NULL                  | Category label (e.g., "Research")  |
| `base_url`     | `TEXT`         | NOT NULL                  | Root URL of the platform           |
| `source_type`  | `VARCHAR(30)`  | NOT NULL                  | `api`, `rss`, `scrape`, `manual`   |
| `priority`     | `SMALLINT`     | DEFAULT 3                 | 1 (highest) to 5 (lowest)         |
| `status`       | `VARCHAR(20)`  | DEFAULT `'active'`        | `active`, `paused`, `retired`      |
| `user_rating`  | `SMALLINT`     | NULLABLE                  | User's 1–5 quality rating          |
| `quality_score`| `NUMERIC(3,2)` | DEFAULT 0.00              | Computed quality metric             |
| `added_at`     | `TIMESTAMP`    | DEFAULT `now()`           | When the source was added           |
| `last_checked` | `TIMESTAMP`    | NULLABLE                  | Last ingestion timestamp            |
| `notes`        | `TEXT`         | NULLABLE                  | Free-form notes                     |

**Indexes:** `idx_sources_status`, `idx_sources_category`

---

### `sub_sources`

Accounts or channels within a source (e.g., a specific arXiv category, GitHub topic).

| Column         | Type           | Constraints                      | Description                          |
|----------------|----------------|----------------------------------|--------------------------------------|
| `id`           | `INTEGER`      | PK, auto-increment               | Unique sub-source identifier         |
| `source_id`    | `INTEGER`      | FK → `sources.id` ON DELETE CASCADE | Parent source                    |
| `platform`     | `VARCHAR(50)`  | NOT NULL                          | Platform identifier                  |
| `handle`       | `VARCHAR(200)` | NOT NULL                          | Channel/account handle               |
| `display_name` | `VARCHAR(200)` | NULLABLE                          | Display label                        |
| `user_rating`  | `SMALLINT`     | NULLABLE                          | User's 1–5 quality rating            |
| `status`       | `VARCHAR(20)`  | DEFAULT `'active'`                | `active`, `paused`                   |
| `last_fetched` | `TIMESTAMP`    | NULLABLE                          | Last fetch time                      |
| `content_count`| `INTEGER`      | DEFAULT 0                         | Number of items fetched              |
| `avg_quality`  | `NUMERIC(3,2)` | DEFAULT 0.00                      | Average quality of fetched content   |
| `added_at`     | `TIMESTAMP`    | DEFAULT `now()`                   | When added                           |

**Constraints:** `uq_sub_source_handle` (source_id + handle unique together)
**Indexes:** `idx_sub_sources_source`, `idx_sub_sources_status`

---

### `content_items`

Individual pieces of content (papers, repos, models, spaces, etc.).

| Column            | Type           | Constraints              | Description                         |
|-------------------|----------------|--------------------------|-------------------------------------|
| `id`              | `INTEGER`      | PK, auto-increment       | Unique content identifier           |
| `source_id`       | `INTEGER`      | FK → `sources.id`, NOT NULL | Originating source              |
| `sub_source_id`   | `INTEGER`      | FK → `sub_sources.id`, NULLABLE | Originating sub-source      |
| `title`           | `TEXT`         | NOT NULL                  | Content title                       |
| `summary`         | `TEXT`         | NULLABLE                  | Description or abstract             |
| `original_url`    | `TEXT`         | UNIQUE, NOT NULL          | Link to original content            |
| `author`          | `VARCHAR(300)` | NULLABLE                  | Author name(s)                      |
| `published_at`    | `TIMESTAMP`    | NULLABLE                  | Original publication date           |
| `fetched_at`      | `TIMESTAMP`    | DEFAULT `now()`           | When we ingested it                 |
| `content_type`    | `VARCHAR(30)`  | NOT NULL                  | `paper`, `repo`, `model`, `space`   |
| `thumbnail_url`   | `TEXT`         | NULLABLE                  | Preview image URL                   |
| `topic_tags`      | `TEXT[]`       | DEFAULT `{}`              | Array of topic labels               |
| `relevance_score` | `NUMERIC(5,4)` | DEFAULT 0.0000            | Computed relevance (0–1)            |
| `engagement_score`| `INTEGER`      | DEFAULT 0                 | Stars, downloads, citations, etc.   |
| `is_read`         | `BOOLEAN`      | DEFAULT false             | User has viewed this item           |
| `is_saved`        | `BOOLEAN`      | DEFAULT false             | User bookmarked this item           |
| `feedback`        | `VARCHAR(10)`  | NULLABLE                  | `up`, `down`, or null               |

**Indexes:** `idx_content_source`, `idx_content_sub_source`, `idx_content_published` (DESC), `idx_content_relevance` (DESC), `idx_content_type`, `idx_content_tags` (GIN)

---

### `feedback_log`

Audit trail for user feedback actions on content items.

| Column       | Type          | Constraints                            | Description            |
|--------------|---------------|----------------------------------------|------------------------|
| `id`         | `INTEGER`     | PK, auto-increment                     | Log entry ID           |
| `content_id` | `INTEGER`     | FK → `content_items.id` ON DELETE CASCADE | Target content item |
| `action`     | `VARCHAR(10)` | NOT NULL                                | `up` or `down`        |
| `created_at` | `TIMESTAMP`   | DEFAULT `now()`                         | When action occurred  |

**Indexes:** `idx_feedback_content`, `idx_feedback_created` (DESC)

---

### `source_change_log`

Audit trail for source configuration edits.

| Column          | Type          | Constraints                            | Description              |
|-----------------|---------------|----------------------------------------|--------------------------|
| `id`            | `INTEGER`     | PK, auto-increment                     | Log entry ID             |
| `source_id`     | `INTEGER`     | FK → `sources.id` ON DELETE CASCADE    | Source that was changed   |
| `field_changed` | `VARCHAR(50)` | NOT NULL                                | Name of the field        |
| `old_value`     | `TEXT`        | NULLABLE                                | Previous value           |
| `new_value`     | `TEXT`        | NULLABLE                                | New value                |
| `reason`        | `TEXT`        | NULLABLE                                | Why the change was made  |
| `changed_at`    | `TIMESTAMP`   | DEFAULT `now()`                         | When the change occurred |

**Indexes:** `idx_changelog_source`

---

### `filter_presets`

Saved filter combinations for quick access.

| Column         | Type           | Constraints        | Description                       |
|----------------|----------------|--------------------|-----------------------------------|
| `id`           | `INTEGER`      | PK, auto-increment | Preset ID                         |
| `name`         | `VARCHAR(100)` | NOT NULL            | Preset display name               |
| `filters_json` | `JSONB`        | NOT NULL            | Serialised filter parameters      |
| `is_default`   | `BOOLEAN`      | DEFAULT false       | Whether this is the default view  |
| `created_at`   | `TIMESTAMP`    | DEFAULT `now()`     | When created                      |

---

## Relationships Summary

| Parent           | Child              | Type        | Cascade       |
|------------------|--------------------|-------------|---------------|
| `sources`        | `sub_sources`      | One-to-Many | DELETE orphan  |
| `sources`        | `content_items`    | One-to-Many | —              |
| `sources`        | `source_change_log`| One-to-Many | DELETE orphan  |
| `sub_sources`    | `content_items`    | One-to-Many | —              |
| `content_items`  | `feedback_log`     | One-to-Many | DELETE orphan  |

---

## Migration Strategy

- **Tool:** Alembic (configured for async with `asyncpg`)
- **Auto-generate:** `make migrate-new msg="description"` detects model changes
- **Apply:** `make migrate` runs all pending migrations
- **Rollback:** `make migrate-down` downgrades by one revision
- **Full reset:** `make dev-reset` drops Docker volumes and recreates from scratch
