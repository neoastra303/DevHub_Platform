# DevHub Platform — Architecture Deep Dive

This document provides a comprehensive technical overview of the DevHub Platform's architecture, covering system design, data flow, security model, API contracts, and operational considerations. It is intended for senior engineers evaluating the project's production-readiness.

---

## 1. System Architecture

DevHub follows a **decoupled service-oriented monolithic architecture** on Django 6.0+. The monolith is organized into distinct layers to enforce separation of concerns without the operational overhead of microservices.

```
┌─────────────────────────────────────────────────────────┐
│                    HTTP / WebSocket                      │
├─────────────────────────────────────────────────────────┤
│  Daphne (ASGI)          │    Gunicorn (WSGI)              │
│  WebSocket Upgrade      │    REST API + HTML Views        │
├─────────────────────────┴────────────────────────────────┤
│                  Django 6.0 Application                   │
│                                                          │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ Views   │ │ ViewSets │ │ Consumers│ │ Celery Tasks │ │
│  │ (HTML)  │ │ (REST)   │ │ (WS)     │ │ (Async)      │ │
│  └────┬────┘ └────┬─────┘ └────┬─────┘ └──────┬──────┘ │
│       │           │            │               │         │
│  ┌────┴───────────┴────────────┴───────────────┴──────┐ │
│  │           Service Layer (services.py)                │ │
│  │           Jobs Layer (jobs.py)                       │ │
│  └───────────────────────┬─────────────────────────────┘ │
│                          │                               │
│  ┌───────────────────────┴─────────────────────────────┐ │
│  │            Models / ORM (12 models)                  │ │
│  └───────────────────────┬─────────────────────────────┘ │
├──────────────────────────┴──────────────────────────────┤
│  PostgreSQL (Production) │ SQLite (Dev) │ Redis (Cache)  │
└──────────────────────────────────────────────────────────┘
```

### 1.1 Request Lifecycle (Example: Create Post)

```
Browser POST /posts/new/
  → URLResolver → PostCreateView.form_valid()
    → Service Layer (via form save)
      → AuditLog.create() via GenericForeignKey
        → Notification broadcast via Channel Layer (WebSocket)
          → Response redirect to feed
```

### 1.2 Async Job Lifecycle (Example: Audit Export)

```
User clicks Export CSV
  → POST /api/v1/devhub/audit/export/
    → BackgroundJob created (status=QUEUED)
      → Celery task dispatched via Redis broker
        → Job processed (status=RUNNING → SUCCEEDED)
          → Notification saved to DB
            → Channel Layer group_send → WebSocket push
              → Frontend receives toast notification
```

---

## 2. Data Layer

### 2.1 Model Design

**12 models** organized around a custom `User` (AbstractUser) with a shared `TimestampedModel` abstract base:

| Model | Type | Key Relationships |
| :--- | :--- | :--- |
| `User` | Concrete (AbstractUser) | Parent of Profile, Project, Post, etc. |
| `Profile` | One-to-One | `user`, M2M `skills` |
| `Project` | Concrete | `owner` (User), M2M `technologies` |
| `Post` | Concrete | `author` (User) |
| `PostMetric` | One-to-One | `post` — aggregated views/likes |
| `PostLike` | Concrete | `user` + `post` (unique constraint) |
| `ViewEvent` | Concrete | `post` + optional `user` |
| `Skill` | Taxonomy | M2M via SkillProficiency |
| `Technology` | Taxonomy | M2M via Project.technologies |
| `TransactionLog` | Concrete | `user`, status workflow |
| `AuditLog` | Concrete | `actor` (User), GenericForeignKey to any model |
| `BackgroundJob` | Concrete | `requested_by` (User), state machine (QUEUED→RUNNING→SUCCEEDED/FAILED) |
| `Comment` | Concrete | `author` (User), FK to Post or Project |
| `Notification` | Concrete | `recipient` (User), boolean `is_read` |

**Indexing Strategy:**
- `db_index=True` on all `slug` fields, `is_featured`, `action`, `status`, `job_type`
- FK fields auto-indexed by Django
- `UniqueConstraint` on PostLike (user + post)
- `unique_together` on SkillProficiency (profile + skill)

### 2.2 Audit Trail (GenericForeignKey)

Every entity lifecycle event is recorded via a GenericForeignKey:

```python
class AuditLog(TimestampedModel):
    actor = ForeignKey(User, on_delete=SET_NULL)
    action = CharField(choices=Action.choices)  # create/update/delete
    content_type = ForeignKey(ContentType)
    object_id = CharField(max_length=64)
    content_object = GenericForeignKey("content_type", "object_id")
    metadata = JSONField(default=dict)
```

This enables querying audit events across any model without polymorphic tables.

---

## 3. API Architecture

### 3.1 REST API (DRF 3.17)

**Base URL:** `/api/v1/devhub/`

**Authentication:** Session-based (same-origin) via DRF's SessionAuthentication.

**Pagination:** PageNumberPagination, 10 per page, configurable via `?page_size=` (max 100).

**Filtering:**
- `django-filter` for structured fields (status, featured, technology slug)
- `SearchFilter` for full-text search on `q` parameter
- Custom `QueryValidationMixin` for safe ordering and choice validation

**Error Contract:** Every error response follows a unified format:

```json
{
  "ok": false,
  "error": {
    "code": "http_400",
    "message": "Unsupported featured 'maybe'.",
    "details": {
      "featured": ["Unsupported featured 'maybe'."]
    }
  }
}
```

Implemented in `devhub_app/api.py` — `devhub_exception_handler` wraps DRF's default handler.

### 3.2 Serializer Design

**Read/Write Separation:** Write serializers enforce stricter validation (title min 3 chars, content min 10 chars, summary min 10 chars, at least one URL on projects). Read serializers include computed fields (`author_name`, `tech_stack`, `target_type`) via `SerializerMethodField` and `source` lookups.

### 3.3 Throttling Strategy

**Two independent layers:**

1. **IP-based (login/signup):** Atomic `check_ip_rate_limit()` using `cache.add` + `cache.incr` — prevents race conditions. Login: 10/5min, Signup: 5/5min.
2. **Per-user (API writes):** DRF `UserRateThrottle` subclasses — `ApiWriteThrottle` (30/hour) + `ApiBurstThrottle` (120/hour). Configurable via environment variables.

---

## 4. Real-time Layer

### 4.1 WebSockets (Django Channels)

**Consumer:** `NotificationConsumer` (AsyncWebsocketConsumer) at `ws://host/ws/notifications/`

**Group naming:** `user_{user.id}_notifications`

**Flow:**
1. Authenticated user connects → added to their notification group
2. Celery task completes → `_push_notification_via_websocket()` called in `jobs.py`
3. `channel_layer.group_send()` → consumer's `send_notification` handler
4. Frontend JS receives JSON → `window.showToast()` + `window.confetti()`

### 4.2 Celery + Redis

**Broker:** Redis (configurable via `CELERY_BROKER_URL`)
**Result Backend:** django-celery-results (database)
**Task Serialization:** JSON
**Key tasks:** `process_background_job_task` — state machine for audit CSV exports

---

## 5. Security Model

### 5.1 Multi-Tenant Data Isolation

**Three layers of defense:**

| Layer | Mechanism | Scope |
| :--- | :--- | :--- |
| QuerySet | `OwnerQuerySetMixin` — `filter(owner=request.user)` | HTML views |
| Object | `IsOwnerObjectPermission` — checks `owner_id`/`author_id`/`user_id` | API viewsets |
| Session | Django's built-in session auth + CSRF | All views |

### 5.2 Production Security Headers

- **HSTS:** 30-day preload (`SECURE_HSTS_SECONDS=2592000`)
- **CSP:** `default-src 'self'`, whitelisted CDNs for scripts/styles/fonts
- **XSS Filter:** Enabled (`SECURE_BROWSER_XSS_FILTER`)
- **Content-Type Sniffing:** Disabled (`SECURE_CONTENT_TYPE_NOSNIFF`)
- **Frame Options:** DENY (`X_FRAME_OPTIONS`)
- **Secure Cookies:** `SESSION_COOKIE_SECURE` + `CSRF_COOKIE_SECURE` in production

### 5.3 Rate Limiting

- Login: 10 attempts per 5 minutes per IP
- Signup: 5 attempts per 5 minutes per IP
- API writes: 30/hour per user (configurable)
- API burst: 120/hour per user (configurable)

---

## 6. DevOps & CI/CD

### 6.1 Containerization

```yaml
# docker-compose.yml
services:
  web:     # Django + Gunicorn, depends on db + redis
  db:      # PostgreSQL 17 with healthcheck
  redis:   # Redis for Celery broker + Channels layer
  celery:  # Celery worker, depends on redis + db
```

### 6.2 CI Pipeline (GitHub Actions)

| Stage | Tool | Command |
| :--- | :--- | :--- |
| Lint | Ruff | `ruff check .` |
| Security | Bandit + pip-audit | `bandit -r . -x ./venv` |
| System checks | Django | `python manage.py check` |
| Migrations | Django | `makemigrations --check --dry-run` |
| Schema | drf-spectacular | `spectacular --file schema.yml` |
| Tests | Django | `python manage.py test` |

### 6.3 Dependencies

- **Python:** Pinned ranges in `requirements.txt` + `pyproject.toml`
- **Node:** Tailwind CSS 3.4 via `package.json`
- **Automation:** Dependabot configured for weekly pip/npm/docker/GitHub Actions updates
- **Pre-commit:** Ruff linting + formatting, YAML/TOML validation, trailing whitespace check

---

## 7. Frontend Architecture

### 7.1 Template System

23 templates organized as:
- **Pages (10):** base, landing, dashboard, feed, profile, project_detail, project_form, post_form, transactions, confirm_delete, audit_logs
- **Components (4):** sidebar, form_field, empty_state, action_button
- **Partials (2):** post_likes (HTMX), job_row (HTMX polling)
- **Auth (7):** login, signup, password reset flow

### 7.2 Static Assets

- **CSS:** Tailwind output + custom `app.css` (glassmorphism, animations, badges, tables)
- **JS Modules (ES6):** `socket_client.js` → orchestrator, `dashboard.js` → Chart.js, `command_palette.js` → keyboard shortcuts, `micro.js` → animations/filters/tooltips, `toast.js` → toast notifications, `client.js` → CSRF-aware fetch wrapper
- **PWA:** `manifest.json` + `service-worker.js` for offline asset caching

### 7.3 External Dependencies

All loaded from CDN: Alpine.js 3.x, HTMX 2.0, Chart.js, Lucide Icons, canvas-confetti, Prism.js

---

## 8. Configuration (12-Factor App)

All environment-specific settings via `django-environ`:

```
DJANGO_SECRET_KEY=           # Required
DJANGO_DEBUG=False           # Default: False
DJANGO_DB_URL=               # Default: sqlite:///db.sqlite3
DJANGO_ALLOWED_HOSTS=        # Default: 127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS= # Default: localhost:8000
CELERY_BROKER_URL=           # Default: memory://
REDIS_URL=                   # Default: redis://localhost:6379/0
DEVHUB_API_WRITE_RATE=       # Default: 30/hour
DEVHUB_API_BURST_RATE=       # Default: 120/hour
DEVHUB_CACHE_ENABLED=False   # Default: False (enables bootstrap caching)
```

---

## 9. Testing Strategy

18 tests across 8 domain-specific test classes:

| Test Class | Focus | Tests |
| :--- | :--- | :--- |
| `PageRenderTests` | Signup, login redirects, authenticated pages | 4 |
| `PostCRUDTests` | Post creation, ownership isolation | 1 |
| `APITests` | Pagination, filtering, validation errors | 4 |
| `ModelRelationshipTests` | Skills/technologies persistence, project+transaction creation | 2 |
| `AuditLogTests` | HTML + API audit creation, page scoping | 2 |
| `RateLimitTests` | API write throttle, login IP throttle | 2 |
| `AuthFlowTests` | Password reset email flow | 1 |
| `BackgroundJobTests` | Queue → process → download lifecycle | 1 |
| `NotificationTests` | Mark-as-read via API action | 1 |
