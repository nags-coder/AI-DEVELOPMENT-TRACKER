# API Reference — AI Pulse

Base URL: `http://localhost:8000/api/v1`

Interactive docs: [Swagger UI](http://localhost:8000/docs) · [ReDoc](http://localhost:8000/redoc)

---

## Health

### `GET /health`

Check API, database, and Redis connectivity.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

## Feed

### `GET /feed`

Paginated, filterable content feed sorted by relevance.

**Query Parameters:**

| Param        | Type     | Default | Description                                              |
|--------------|----------|---------|----------------------------------------------------------|
| `page`       | int      | 1       | Page number (1-based)                                    |
| `size`       | int      | 20      | Items per page (max 100)                                 |
| `source_id`  | int      | —       | Filter by source ID                                      |
| `type`       | string   | —       | Filter by content type (`paper`, `repo`, `model`, `space`) |
| `time_range` | string   | —       | Filter by age: `today`, `7d`, `30d`                      |
| `search`     | string   | —       | Full-text search in title and summary                    |
| `sort`       | string   | `score` | Sort order: `score`, `date`, `engagement`                |

**Response** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "title": "Attention Is All You Need",
      "summary": "...",
      "original_url": "https://arxiv.org/abs/2202.01169",
      "author": "Author Name",
      "published_at": "2024-12-01T10:00:00",
      "content_type": "paper",
      "source_name": "arXiv",
      "relevance_score": 0.8521,
      "engagement_score": 1500,
      "topic_tags": ["transformers", "nlp"],
      "is_read": false,
      "is_saved": false,
      "feedback": null
    }
  ],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

### `GET /feed/must-read`

Returns the single highest-scored content item from today.

**Response** `200 OK`
```json
{
  "id": 42,
  "title": "...",
  "summary": "...",
  "original_url": "...",
  "relevance_score": 0.9231,
  ...
}
```

**Response** `404 Not Found` — No content available for today.

---

## Sources

### `GET /sources`

List all content sources.

**Response** `200 OK`
```json
[
  {
    "id": 4,
    "name": "arXiv",
    "category": "Research",
    "base_url": "https://arxiv.org",
    "source_type": "api",
    "priority": 1,
    "status": "active",
    "user_rating": null,
    "quality_score": 0.0,
    "added_at": "2024-12-01T00:00:00",
    "last_checked": "2024-12-15T12:30:00"
  }
]
```

### `POST /sources`

Create a new source.

**Request Body:**
```json
{
  "name": "Hacker News",
  "category": "News",
  "base_url": "https://news.ycombinator.com",
  "source_type": "api",
  "priority": 3
}
```

**Response** `201 Created` — Returns the created source object.

### `PUT /sources/:id`

Update an existing source. All fields in the body replace existing values.

**Path Parameters:** `id` (int) — Source ID

**Request Body:** Same schema as POST (partial updates supported).

**Response** `200 OK` — Returns the updated source object.

### `DELETE /sources/:id`

Soft-delete a source (sets `status` to `retired`).

**Path Parameters:** `id` (int) — Source ID

**Response** `200 OK`

---

## Sub-Sources

### `GET /sub-sources`

List all sub-sources (channels/accounts within sources).

**Response** `200 OK`
```json
[
  {
    "id": 1,
    "source_id": 4,
    "platform": "arxiv",
    "handle": "cs.AI",
    "display_name": "Artificial Intelligence",
    "user_rating": null,
    "status": "active",
    "content_count": 25
  }
]
```

### `POST /sub-sources`

Create a new sub-source.

**Request Body:**
```json
{
  "source_id": 4,
  "platform": "arxiv",
  "handle": "cs.CL",
  "display_name": "Computation and Language"
}
```

**Response** `201 Created`

### `PATCH /sub-sources/:id/rate`

Rate a sub-source (1–5 stars).

**Request Body:**
```json
{
  "rating": 4
}
```

**Response** `200 OK`

---

## Content

### `GET /content/:id`

Get a single content item by ID.

**Path Parameters:** `id` (int) — Content item ID

**Response** `200 OK` — Full content item object.

### `POST /content/:id/feedback`

Submit feedback (thumbs up or down) on a content item.

**Request Body:**
```json
{
  "action": "up"
}
```

| Field    | Type   | Values       |
|----------|--------|--------------|
| `action` | string | `up`, `down` |

**Response** `200 OK`

### `POST /content/:id/save`

Bookmark a content item (`is_saved = true`).

**Response** `200 OK`

### `DELETE /content/:id/save`

Remove bookmark from a content item (`is_saved = false`).

**Response** `200 OK`

---

## Ingestion

### `POST /ingest/trigger`

Trigger ingestion for **all active sources**. Dispatches Celery tasks.

**Response** `200 OK`
```json
{
  "message": "Ingestion triggered for all sources",
  "task_ids": ["abc-123", "def-456"]
}
```

### `POST /ingest/trigger/:source_id`

Trigger ingestion for a **single source**.

**Path Parameters:** `source_id` (int) — Source ID

**Response** `200 OK`
```json
{
  "message": "Ingestion triggered for source 4",
  "task_id": "abc-123"
}
```

### `POST /ingest/score`

Re-score all content items using the scoring engine.

**Response** `200 OK`
```json
{
  "message": "Scored 150 items"
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{
  "detail": "Source not found"
}
```

| Status Code | Meaning                       |
|-------------|-------------------------------|
| 400         | Bad request / validation error |
| 404         | Resource not found             |
| 422         | Unprocessable entity           |
| 500         | Internal server error          |
