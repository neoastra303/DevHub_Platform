# DevHub Platform | Enterprise-Grade Developer Workspace

[![CI](https://github.com/neoastra303/DevHub_Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/neoastra303/DevHub_Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Django: 6.0](https://img.shields.io/badge/Django-6.0-green.svg)](https://docs.djangoproject.com/en/6.0/)

DevHub is a **production-hardened, event-driven developer workspace** engineered for scalability, real-time interactivity, and high-fidelity data visualization. It serves as a showcase for modern backend engineering, robust API design, and professional DevOps practices.

Created and maintained by [neoastra303](https://github.com/neoastra303).

---

## 🌟 Project Highlights

*   **Engineered for Scale:** Asynchronous task processing via **Celery & Redis**; real-time notifications with **Django Channels (WebSockets)**.
*   **Modern, Interactive UI:** Implemented **HTMX** for seamless, partial page updates and **Chart.js** for deep data-driven user insights.
*   **Enterprise-Grade Security:** Dual-layer API rate limiting, IP-based protection on auth endpoints, and hardened security headers (HSTS, CSRF).
*   **Observability First:** Real-time system monitoring integrated via **Prometheus**.
*   **Automated Quality Assurance:** CI/CD pipeline enforcing strict linting (**Ruff**), security scanning (**Bandit**), and comprehensive test coverage.

---

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend** | Django 6.0, Django REST Framework, Celery |
| **Frontend** | Tailwind CSS 3.4, HTMX, Alpine.js, Chart.js |
| **Real-time** | Redis, Django Channels (WebSockets) |
| **Observability** | Prometheus |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **API Docs** | drf-spectacular (OpenAPI 3.0) |

---

## 🚦 Getting Started

### Using Docker (Recommended)

```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### API Documentation
Once running, explore the API through:
- **Swagger UI:** `/api/docs/swagger/` (Points to `/api/v1/devhub/`)
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

---

## 🔒 Security Policy
For reporting vulnerabilities, please refer to our [Security Policy](SECURITY.md).
