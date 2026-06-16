<p align="center">
  <img src="Social%20Banner.png" alt="DevHub Platform" width="800">
</p>

<p align="center">
  <a href="https://github.com/neoastra303/DevHub_Platform/actions"><img src="https://github.com/neoastra303/DevHub_Platform/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/release/python-3130/"><img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python 3.13"></a>
  <a href="https://docs.djangoproject.com/en/6.0/"><img src="https://img.shields.io/badge/Django-6.0-green.svg" alt="Django 6.0"></a>
  <a href="https://htmx.org/"><img src="https://img.shields.io/badge/HTMX-2.0-ff69b4.svg" alt="HTMX 2.0"></a>
  <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg" alt="Tailwind 3.4"></a>
  <br>
  <a href="#key-features"><img src="https://img.shields.io/badge/status-production--ready-73f5c8.svg" alt="Status"></a>
  <a href="https://github.com/neoastra303/DevHub_Platform/tree/main/devhub_app/tests.py"><img src="https://img.shields.io/badge/tests-18%20passing-brightgreen.svg" alt="Tests"></a>
  <a href="https://www.django-rest-framework.org/"><img src="https://img.shields.io/badge/DRF-3.17-red.svg" alt="DRF 3.17"></a>
</p>

---

**DevHub Platform** is a production-hardened, full-stack developer workspace engineered with Django 6.0, Celery, and HTMX. It provides a frictionless, event-driven environment for project tracking, real-time analytics, and data visualization — designed to transform the chaos of modern engineering into a calm, structured narrative.

> Built by [neoastra303](https://github.com/neoastra303)

---

## Key Features

<p align="center">
  <img src="Features%20Grid.png" alt="Features" width="800">
</p>

### Core Workspace
- **Project Management** — Full CRUD with technology tagging, featured projects, and slug-based routing
- **Post Feed** — Rich-text posts with like tracking, view analytics, and ownership scoping
- **Transaction Logging** — Financial tracking with status workflows (pending/completed/failed)
- **Profile Management** — Skills taxonomy, reputation scoring, avatar customization

### Real-time & Async
- **WebSocket Notifications** — Live push via Django Channels when background jobs complete
- **Celery Task Queue** — Async CSV exports and background processing with Redis broker
- **HTMX Interactivity** — Partial page updates for likes, job status polling, and seamless UX

### Security & Observability
- **Dual-Layer Rate Limiting** — Atomic IP-based throttling for login/signup + DRF per-user throttling
- **Audit Trail** — GenericForeignKey-based logging of every Create/Update/Delete with actor metadata
- **Multi-Tenant Isolation** — QuerySet-level scoping + object-level permissions
- **CSP Headers** — Content Security Policy for XSS mitigation
- **Prometheus Metrics** — django-prometheus integration for system monitoring

### API & Documentation
- **RESTful API** — DRF with ViewSets, pagination, filtering, and structured error contracts
- **OpenAPI 3.0** — Auto-generated schema via drf-spectacular (Swagger UI + Redoc)
- **Unified Error Format** — Every API response follows `{"ok": bool, "error": {...}}` contract

---

## Tech Stack

<p align="center">
  <img src="Tech%20Stack%20Showcase.png" alt="Tech Stack" width="800">
</p>

| Layer | Technology |
| :--- | :--- |
| **Backend** | Django 6.0, Django REST Framework 3.17, Celery 5.4 |
| **Frontend** | Tailwind CSS 3.4, HTMX 2.0, Alpine.js 3.x, Chart.js, Lucide Icons |
| **Real-time** | Django Channels 4.1, Redis, WebSockets |
| **Database** | PostgreSQL 17 (production), SQLite (development) |
| **Observability** | Prometheus, django-prometheus |
| **DevOps** | Docker, Docker Compose, Gunicorn, WhiteNoise |
| **CI/CD** | GitHub Actions — Ruff linting, Bandit security, 18-test suite, migration checks |
| **Tooling** | Pre-commit hooks, Ruff formatter, Dependabot |

---

## Architecture

<p align="center">
  <img src="Architecture%20Diagram.png" alt="Architecture" width="800">
</p>

DevHub follows a **decoupled service-oriented monolithic architecture**:

```
DevHub_Platform/
├── core/                  # Project configuration
│   ├── settings/          # 12-factor settings (base/dev/prod)
│   ├── middleware.py      # CSP security headers
│   ├── celery.py          # Celery application
│   ├── asgi.py            # ASGI for Channels + HTTP
│   └── wsgi.py            # WSGI for Gunicorn
├── devhub_app/            # Main application
│   ├── models.py          # 12 models (User, Project, Post, AuditLog, etc.)
│   ├── views.py           # HTML views + DRF API viewsets
│   ├── serializers.py     # 11 serializers with read/write separation
│   ├── services.py        # Business logic layer (bootstrap, etc.)
│   ├── jobs.py            # Celery background jobs + WebSocket push
│   ├── throttling.py      # Atomic rate limiting
│   ├── permissions.py     # Object-level ownership permissions
│   ├── consumers.py       # WebSocket notification consumer
│   ├── audit.py           # GenericForeignKey audit logging
│   ├── filters.py         # DRF filter backends
│   ├── api.py             # Unified exception handler
│   ├── forms.py           # 5 form classes
│   ├── admin.py           # Admin configuration
│   ├── tests.py           # 18 tests across 8 domain classes
│   └── api_urls.py        # REST API routing
├── templates/             # 23 Jinja templates with component architecture
├── static/                # CSS, JS modules, PWA manifest, service worker
├── design/                # Database schema documentation
├── plans/                 # UI/UX implementation plans
└── .github/               # CI workflows + Dependabot config
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full architectural deep dive.

---

## Quick Start

### Using Docker (Recommended)

```bash
docker-compose up --build
```

Available at `http://localhost:8000`.

### Manual Setup

```bash
# 1. Clone and enter
git clone https://github.com/neoastra303/DevHub_Platform.git
cd DevHub_Platform

# 2. Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure
cp .env.example .env       # Edit DJANGO_SECRET_KEY and DB settings

# 4. Database
python manage.py migrate

# 5. Run
python manage.py runserver

# 6. (Optional) Celery worker for async jobs
celery -A core worker -l info
```

### Demo Access

The app auto-seeds a demo user on first visit:
- **Username:** `demo`
- **Password:** `demo-password-123`

---

## API Overview

The REST API is available at `/api/v1/devhub/`:

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `posts/` | GET/POST | List or create posts |
| `posts/{id}/` | GET/PUT/PATCH/DELETE | Post CRUD |
| `projects/` | GET/POST | List or create projects |
| `projects/{id}/` | GET/PUT/PATCH/DELETE | Project CRUD |
| `audit/` | GET | Paginated audit log |
| `audit/export/` | POST | Queue CSV export |
| `jobs/` | GET | List background jobs |
| `jobs/{id}/download/` | GET | Download job result |
| `dashboard-summary/` | GET | Dashboard metrics |
| `analytics/` | GET | 7-day view analytics |
| `profile/skills/` | GET | Radar chart data |
| `transactions/` | GET | Filtered transaction list |
| `notifications/` | GET | User notifications |

**Interactive Docs:**
- Swagger UI: `/api/docs/swagger/`
- Redoc: `/api/docs/redoc/`

---

## Testing

```bash
# Run full suite (18 tests across 8 domain classes)
python manage.py test

# Run specific domain
python manage.py test devhub_app.tests.AuditLogTests
python manage.py test devhub_app.tests.RateLimitTests

# Security scan
bandit -r . -x ./venv

# Linting
ruff check . --fix
```

The test suite covers: page rendering, authentication flows, CRUD ownership isolation, API pagination/filtering, audit logging (HTML + API), rate limiting (login + API), password reset flow, health checks, background job lifecycle (queue → process → download), and notification read tracking.

---

## Project Roadmap

<p align="center">
  <img src="DevHub%20Roadmap.png" alt="Roadmap" width="800">
</p>

### Completed
- Service-oriented architecture with 12 models and full CRUD
- RESTful API with pagination, filtering, and structured error contracts
- Dual-layer rate limiting (IP-based + per-user) with atomic operations
- GenericForeignKey audit trail for all entity lifecycle events
- Celery background job processing with CSV exports
- WebSocket real-time notifications via Django Channels
- PWA manifest + service worker for offline asset caching
- Content Security Policy headers for XSS mitigation
- 18-test suite across 8 domain-specific test classes
- CI/CD with Ruff, Bandit, migration checks, and schema validation

### In Progress
- Enhanced analytics dashboard with time-series visualizations
- Social features (follows, collaborative projects)
- Advanced job scheduling with retry logic

---

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for our engineering standards, testing policy, and submission process. This project maintains a high bar — all contributions must pass CI (Ruff, Bandit, 18 tests).

---

## Security

For vulnerability reporting, see [SECURITY.md](SECURITY.md). We take security seriously — audit logging, CSP, rate limiting, and data isolation are first-class concerns.

---

## License

[MIT](LICENSE) © neoastra303
