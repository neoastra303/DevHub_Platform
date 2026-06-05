# DevHub Platform | Enterprise-Grade Developer Workspace

[![CI](https://github.com/neoastra303/DevHub_Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/neoastra303/DevHub_Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Django: 6.0](https://img.shields.io/badge/Django-6.0-green.svg)](https://docs.djangoproject.com/en/6.0/)

DevHub is a production-hardened Django platform designed to demonstrate advanced back-end engineering, robust API design, and modern DevOps practices. It provides a multi-tenant workspace for developers to manage projects, posts, and transactions with full auditability and security.

Created and maintained by [neoastra303](https://github.com/neoastra303).

---

## 🏛️ Architecture & Design

This project goes beyond basic CRUD, implementing enterprise patterns such as:
- **Service Layer Pattern:** Business logic decoupled from views.
- **Relational Taxonomy:** Normalized many-to-many schema for skills and tech stacks.
- **Advanced Security:** Custom throttling, multi-tenant isolation, and automated audit trails.

**For a deep dive into the system design, see [ARCHITECTURE.md](ARCHITECTURE.md).**

---

## 🚀 Key Features

### 🔹 Advanced Backend Engineering
- **Multi-Tenant Isolation:** Data is strictly scoped to the owner using custom Mixins and Permission classes.
- **Audit Logging System:** Automated tracking of all Create/Update/Delete actions with rich metadata.
- **Background Jobs:** Asynchronous workflow for resource-heavy tasks like audit log exports.
- **Standardized API Contracts:** Unified error handling and response structures for a professional API consumer experience.

### 🔹 Security & Protection
- **Dual-Layer Throttling:** Configurable burst and sustained rate limits for API write operations.
- **IP-Based Protection:** Rate limiting on sensitive endpoints like Login and Signup.
- **Production Hardening:** HSTS, Secure Cookies, XSS filtering, and CSRF protection are active by default.

### 🔹 DevOps & Quality Assurance
- **Dockerized Ecosystem:** Multi-container orchestration (Django + PostgreSQL) with health-check-dependent startup.
- **Automated CI/CD:** GitHub Actions pipeline running `Ruff` (linting), `Bandit` (security scanning), and full test suites.
- **API Documentation:** Integrated **Swagger UI** and **Redoc** for standardized OpenAPI 3.0 documentation.

---

## 🛠️ Tech Stack

- **Framework:** Django 6.0 & Django REST Framework (DRF)
- **Database:** PostgreSQL (Production), SQLite (Local Dev)
- **Tooling:** Docker & Docker Compose
- **Quality:** Ruff, Bandit, GitHub Actions
- **API Docs:** drf-spectacular (OpenAPI 3.0)

---

## 🚦 Getting Started

### Using Docker (Recommended)

```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### API Documentation
Once running, explore the API through:
- **Swagger UI:** `/api/docs/swagger/`
- **Redoc:** `/api/docs/redoc/`

---

## 🧪 Testing & Validation

```bash
# Run full test suite (Django + REST API)
python manage.py test

# Run security scan
bandit -r . -x ./venv

# Lint and format
ruff check . --fix
```

## 🔒 Security

For reporting vulnerabilities, please refer to our [Security Policy](SECURITY.md).
