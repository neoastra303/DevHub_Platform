# Contributing to DevHub Platform

Thank you for your interest in contributing! We welcome pull requests from everyone.

## Development Workflow

1. **Fork the Repo:** Create your own fork of the project.
2. **Clone:** Clone the fork to your local machine.
3. **Setup Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create a Branch:** Create a branch for your changes (`git checkout -b feature/amazing-feature`).
5. **Develop:** Make your changes and ensure they follow the project style.
6. **Test:** Run the full test suite:
   ```bash
   python manage.py test
   ```
7. **Commit:** Commit your changes with a clear message.
8. **Push & PR:** Push to your fork and submit a Pull Request.

## Code Standards

- Follow PEP 8 guidelines.
- Ensure all new features are accompanied by unit tests.
- Keep the API documentation (OpenAPI) updated if you modify endpoints.

## Security

Please refer to our [Security Policy](SECURITY.md) for reporting vulnerabilities.
