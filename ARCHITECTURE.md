# DevHub Platform | Architectural Design Document

This document outlines the architectural patterns, technical decisions, and security implementations of the DevHub Platform. It is designed to demonstrate high-level engineering principles and production-readiness.

## 🏛️ System Architecture

DevHub follows a decoupled, service-oriented monolithic architecture built on Django.

### 1. Service Layer Pattern
To maintain lean models and views, business logic is encapsulated within the `services.py` and `jobs.py` modules. 
- **Bootstrapping:** Automated idempotent data seeding.
- **Background Processing:** Decoupled job execution for resource-intensive operations (e.g., CSV exports).

### 2. Relational Database Design
The schema is designed for scalability and data integrity:
- **Abstract Base Models:** `TimestampedModel` ensures consistent audit trailing across all entities.
- **Normalized Taxonomy:** `Skill` and `Technology` are implemented as independent entities with many-to-many relationships, optimized via `prefetch_related`.
- **Slug Management:** Automated, collision-resistant slug generation for SEO-friendly and user-friendly URLs.

### 3. API Design & Standardized Contracts
The REST API is powered by Django REST Framework (DRF) with a focus on consistency:
- **Unified Exception Handling:** A custom `devhub_exception_handler` ensures every error response follows a predictable `{ "ok": False, "error": { ... } }` contract.
- **Throttling Strategy:** Dual-layer throttling using `ApiWriteThrottle` (30/hr) and `ApiBurstThrottle` (120/hr) to protect system resources.
- **Query Validation:** Custom `QueryValidationMixin` for rigorous validation of pagination and ordering parameters.

## 🛡️ Security & Observability

### 1. Multi-Tenant Data Isolation
Data is strictly scoped to the authenticated user.
- **QuerySet Scoping:** `OwnerQuerySetMixin` ensures users can only access their own data at the database query level.
- **Object-Level Permissions:** `IsOwnerObjectPermission` provides a secondary defense layer for API actions.

### 2. Audit & Compliance
The platform implements a comprehensive **Audit Trail**:
- Every critical lifecycle event (Create, Update, Delete) is logged with an actor, timestamp, and metadata.
- **API Audit:** Specific metadata flags identify actions originating from the REST API vs. the Web UI.

### 3. Hardened Security Configuration
- **HSTS & Secure Cookies:** Enforced in production to prevent session hijacking and man-in-the-middle attacks.
- **Rate Limiting:** IP-based throttling for sensitive endpoints (Login/Signup) to mitigate brute-force attacks.

## ⚙️ DevOps & CI/CD

### 1. Containerization
- **Multi-Container Setup:** Docker Compose orchestrates the Django application and a PostgreSQL database.
- **Health Checks:** Native Docker health checks ensure the database is ready before the application starts.

### 2. Continuous Integration
The GitHub Actions pipeline (`ci.yml`) enforces three pillars of quality:
- **Linting:** `Ruff` for Pythonic code standards.
- **Security:** `Bandit` for static analysis of security vulnerabilities.
- **Functional Testing:** Full Django test suite with automated migration checks.

## 🚀 Future Roadmap
- **Real-time Notifications:** Integration with Django Channels for WebSocket-based updates.
- **Enhanced Observability:** Implementation of Prometheus/Grafana for real-time system monitoring.
- **Advanced Job Scheduling:** Migration from manual processing to Redis/Celery for better throughput.
