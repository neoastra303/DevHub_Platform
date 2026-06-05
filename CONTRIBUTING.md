# Contributing to DevHub Platform

Thank you for your interest in contributing to DevHub Platform! This project maintains high engineering standards to ensure production reliability.

## 🛠️ Development Setup

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/your-username/DevHub_Platform.git
   cd DevHub_Platform
   ```

2. **Environment Setup:**
   We recommend using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Initialization:**
   ```bash
   python manage.py migrate
   ```

## 📏 Engineering Standards

### 1. Code Style
- We use **Ruff** for linting and formatting.
- Ensure your code passes `ruff check .` before submitting.
- Follow PEP 8 guidelines and maintain clear, descriptive naming conventions.

### 2. Testing Policy
- **Coverage:** All new features must be accompanied by unit or integration tests in `devhub_app/tests.py`.
- **Regression:** Run the full suite with `python manage.py test` to ensure no regressions.

### 3. API Changes
- If you modify API endpoints, ensure the OpenAPI schema remains accurate.
- Run `python manage.py spectacular --file schema.yml` to verify schema generation if necessary.

### 4. Security
- Never commit sensitive data or hardcoded secrets.
- Use the `record_audit_event` service for any new critical entity lifecycle changes.
- Refer to [SECURITY.md](SECURITY.md) for vulnerability reporting.

## 🚀 Submission Process

1. Create a feature branch: `git checkout -b feat/your-feature-name`.
2. Commit your changes with [Conventional Commits](https://www.conventionalcommits.org/).
3. Push to your fork and open a Pull Request (PR) against the `main` branch.
4. Ensure the CI pipeline passes all stages (Lint, Security, Test).

## 🏛️ Architecture Guidance
Before making significant structural changes, please review the [ARCHITECTURE.md](ARCHITECTURE.md) to understand the service-layer and multi-tenancy patterns used in this project.
