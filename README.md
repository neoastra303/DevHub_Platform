# DevHub Platform | Enterprise-Grade Developer Workspace

[![CI](https://github.com/neoastra303/DevHub_Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/neoastra303/DevHub_Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DevHub is a production-ready Django platform designed to showcase advanced back-end engineering, database architecture, and DevOps practices.

Created and maintained by [neoastra303](https://github.com/neoastra303).

## 🚀 Key Engineering Features

- **Multi-Tenant Architecture:** Per-user isolated dashboards, feeds, and project management.
- **RESTful API (DRF):** Fully authenticated API with custom serializers, viewsets, and structured error handling.
- **Production Hardening:** 
  - **Security:** HSTS, Secure Cookies, XSS Filtering, and CSRF protection.
  - **Rate Limiting:** IP-based throttling for Login, Signup, and API write operations.
  - **Audit Logging:** System-wide audit trail for critical entity lifecycle events (Create/Update/Delete).
- **Asynchronous Workflows:** Custom background job system for resource-intensive tasks (e.g., Audit Exports).
- **API Documentation:** Integrated **Swagger** and **Redoc** via `drf-spectacular` for standardized OpenAPI documentation.
- **DevOps & Containerization:** 
  - **Dockerized:** Multi-container setup (Django + PostgreSQL) using Docker Compose.
  - **Health Monitoring:** Dedicated health check endpoint for zero-downtime deployments.
  - **CI/CD:** GitHub Actions for automated testing, migration consistency, and security checks.

## 🛠️ Tech Stack

- **Backend:** Django 6.0, Django REST Framework
- **Database:** PostgreSQL (Production), SQLite (Development)
- **Containerization:** Docker, Docker Compose
- **Documentation:** OpenAPI 3.0 (Swagger/Redoc)
- **CI/CD:** GitHub Actions

## 🚦 Getting Started

### Using Docker (Recommended)

```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### Manual Local Setup

1. **Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   Copy `.env.example` to `.env` and configure your variables.

3. **Database Setup:**
   ```bash
   python manage.py migrate
   ```

4. **Run Server:**
   ```bash
   python manage.py runserver
   ```

## 📖 API Documentation

- **Swagger UI:** `/api/docs/swagger/`
- **Redoc:** `/api/docs/redoc/`
- **OpenAPI Schema:** `/api/schema/`

## 🧪 Testing & Quality Assurance

```bash
# Run full test suite
python manage.py test

# Process background jobs manually
python manage.py process_jobs

# Check system health
curl http://localhost:8000/health/
```

## 🔒 Security & Compliance

The platform implements industry-standard security headers and best practices to ensure data integrity and user protection. Audit logs provide a transparent history of all administrative actions.
