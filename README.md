# DevHub Platform | Your Dev Life, Optimized.

[![CI](https://github.com/neoastra303/DevHub_Platform/actions/workflows/ci.yml/badge.svg)](https://github.com/neoastra303/DevHub_Platform/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Django: 6.0](https://img.shields.io/badge/Django-6.0-green.svg)](https://docs.djangoproject.com/en/6.0/)

---

![DevHub Social Banner](Social%20Banner.png)

---

DevHub is more than a dashboard; it’s the quiet, high-performance vault for your technical journey. We believe in the power of focus, the joy of organized code, and the necessity of real-time insights—all delivered with zero friction.

Whether you're tracking intricate project dependencies or simply need a clean space to breathe and build, DevHub transforms the chaos of modern engineering into a calm, structured narrative.

Created with heart by [neoastra303](https://github.com/neoastra303).

---

## 🌟 Features at a Glance

![Features Grid](Features%20Grid.png)

We don't just build features; we craft experiences that respect your time and intellect.

*   **⚡ Built for Velocity:** Asynchronous task processing (Celery & Redis) ensures that your workspace stays snappy.
*   **✨ Interactive & Alive:** Feel the responsiveness of **HTMX** for seamless, partial page updates, while **Chart.js** turns raw data into a beautiful, meaningful story.
*   **🛡️ Your Digital Sanctuary:** With dual-layer rate limiting and hardened security headers, your intellectual property remains private and secure.
*   **🔭 Total Observability:** Real-time system monitoring via **Prometheus** means you’re always in tune with the health and performance of your platform.

---

## 🗺️ Roadmap

![DevHub Roadmap](DevHub%20Roadmap.png)

---

## 🛠️ The Engine Under the Hood

![Tech Stack Showcase](Tech%20Stack%20Showcase.png)

| Component | Technology |
| :--- | :--- |
| **Backend** | Django 6.0, Django REST Framework, Celery |
| **Frontend** | Tailwind CSS 3.4, HTMX, Alpine.js, Chart.js |
| **Real-time** | Redis, Django Channels (WebSockets) |
| **Observability** | Prometheus |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **API Docs** | drf-spectacular (OpenAPI 3.0) |

![Architecture Diagram](Architecture%20Diagram.png)

---

## 🚦 Getting Started

Ready to experience a more organized dev life?

### Using Docker (The Easiest Route)

```bash
docker-compose up --build
```
Your new workspace will be waiting for you at `http://localhost:8000`.

### API Documentation
Dive into the technical specs:
- **Swagger UI:** `/api/docs/swagger/`
- **Redoc:** `/api/docs/redoc/`

---

## 🧪 Quality & Assurance

We maintain a high bar because your code deserves it.

```bash
# Validate everything
python manage.py test

# Security first
bandit -r . -x ./venv

# Keep it polished
ruff check . --fix
```

---

## 🔒 Security Policy
Trust is the foundation of every great partnership. For reporting vulnerabilities, please refer to our [Security Policy](SECURITY.md).
