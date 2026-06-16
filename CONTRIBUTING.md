# Contributing to DevHub Platform

Thank you for your interest in contributing. This project maintains production-grade engineering standards. Please follow the guidelines below.

---

## Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/DevHub_Platform.git
cd DevHub_Platform

# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install  # Tailwind CSS for frontend

# Environment configuration
cp .env.example .env
# Edit DJANGO_SECRET_KEY and database settings

# Initialize database
python manage.py migrate

# Build Tailwind CSS
npm run build:css

# Start development server
python manage.py runserver

# (Optional) Celery worker for async jobs
celery -A core worker -l info
```

### Pre-commit Hooks

The project includes a `.pre-commit-config.yaml` with Ruff linting/formatting and general checks. Install the hooks:

```bash
pip install pre-commit
pre-commit install
```

---

## Code Style & Standards

### Python
- **Formatter:** Ruff (matches `pyproject.toml` config: line-length 120, target Python 3.13)
- **Lint checks:** `ruff check . --fix` before committing
- **Naming:** Descriptive, PEP 8 compliant. Avoid single-letter variables except in comprehensions.
- **Imports:** Grouped as stdlib → third-party → Django → local. Ruff's isort handles this.

### Django
- **Models:** Extend `TimestampedModel` for audit trails. Add `__str__` and `__repr__`.
- **Views:** Prefer class-based views for HTML; function-based `@api_view` for simple API endpoints.
- **Business logic:** Put it in `services.py` or `jobs.py`, not in views or models.
- **Audit logging:** Call `record_audit_event()` for every entity Create/Update/Delete.
- **Permissions:** Use `OwnerQuerySetMixin` + `IsOwnerObjectPermission` for data isolation.

### JavaScript (ES6 modules)
- Located in `static/js/` organized as `api/`, `features/`, `ui/`
- Use `window.*` exports sparingly — prefer module imports
- CSRF tokens: use the `apiFetch()` wrapper from `static/js/api/client.js`

### Frontend (Templates)
- Extend `devhub_app/base.html` for authenticated pages
- Use component includes: `form_field.html`, `action_button.html`, `empty_state.html`
- HTMX for partial updates; Alpine.js for client-side state; avoid jQuery

---

## Testing

### Running Tests

```bash
# Full suite (18 tests across 8 domain classes)
python manage.py test

# Domain-specific
python manage.py test devhub_app.tests.AuditLogTests
python manage.py test devhub_app.tests.RateLimitTests
python manage.py test devhub_app.tests.BackgroundJobTests

# Verbose
python manage.py test -v2
```

### Test Organization

Tests are split by domain in `devhub_app/tests.py`:

| Class | Coverage |
| :--- | :--- |
| `PageRenderTests` | Page rendering, login redirects, health check |
| `PostCRUDTests` | Post creation and ownership isolation |
| `APITests` | Pagination, filtering, validation, error contracts |
| `ModelRelationshipTests` | Skills/technologies persistence |
| `AuditLogTests` | Audit creation (HTML + API), page scoping |
| `RateLimitTests` | API write throttle, login IP throttle |
| `AuthFlowTests` | Password reset email flow |
| `BackgroundJobTests` | Job lifecycle: queue → process → download |
| `NotificationTests` | Mark-as-read API action |

### Test Guidelines
- Every new feature requires a corresponding test
- Use `self.login()` from `BaseTestCase` for authenticated requests
- Use `@override_settings` for throttle/rate tests
- Ensure cache isolation with `cache.clear()` in `setUp` for rate limit tests

---

## API Changes

If you modify API endpoints:

```bash
# Verify OpenAPI schema generation
python manage.py spectacular --file schema.yml

# Check that existing API tests still pass
python manage.py test devhub_app.tests.APITests
```

All API responses must follow the unified error contract (`{"ok": false, "error": {"code": ..., "message": ..., "details": ...}}`).

---

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

<optional body>

<optional footer>
```

**Types:** `feat`, `fix`, `perf`, `test`, `docs`, `chore`, `refactor`, `style`, `ci`

**Examples:**
```
feat: add WebSocket notification push for background jobs
fix: correct AuditLog field references in CSV export
perf: move aggregate query outside analytics loop
test: split monolithic test class into domain classes
docs: add architecture deep-dive document
```

---

## Pull Request Process

1. Create a branch: `git checkout -b feat/your-feature`
2. Make changes with descriptive commits
3. Ensure all CI stages pass: Ruff → Bandit → Django checks → migrations → tests
4. Open a PR against `main` with a clear description of the change and its motivation
5. Link related issues if applicable

---

## Architecture Reference

Before making structural changes, review:
- [ARCHITECTURE.md](ARCHITECTURE.md) — system design, data flow, security model
- `design/db_schema_v2.md` — database schema evolution
- `plans/ui_upgrades.md` — frontend implementation plans
