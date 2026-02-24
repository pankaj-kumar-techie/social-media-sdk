# Contributing to Social Media SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

---

## 🐛 Reporting Issues

1. Check existing [issues](https://github.com/yourusername/social-media-sdk/issues) to avoid duplicates
2. Use a clear, descriptive title
3. Include:
   - Python version (`python --version`)
   - OS and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant log output (mask any credentials)

---

## 🔀 Pull Request Process

### 1. Fork & Clone

```bash
git clone https://github.com/your-fork/social-media-sdk.git
cd social-media-sdk
pip install -e .
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Code Standards

- **Python 3.10+** — Use modern type hints (`str | None` over `Optional[str]`)
- **PEP 8** — Follow standard Python style conventions
- **Type hints** — All function signatures must have complete type annotations
- **Docstrings** — Google-style docstrings for all public methods
- **Logging** — Use `loguru.logger`, never `print()`
- **No raw HTTP** — All requests go through `AsyncHttpClient`

### 4. Commit Messages

Use clear, conventional commit messages:

```
feat: add Twitter/X platform client
fix: handle empty pageToken in YouTube pagination
docs: add rate limiting configuration guide
refactor: extract pagination logic into base class
```

### 5. Submit Your PR

- Push your branch and open a Pull Request
- Fill in the PR template with a description of changes
- Ensure all existing functionality still works
- Add documentation for new features

---

## 🏗️ Architecture Guidelines

When adding new features, follow these principles:

1. **Platform clients** inherit `BasePlatformClient` and implement `get_profile()` + `get_all_content()`
2. **Data models** use Pydantic — add fields to existing models or create new ones
3. **HTTP requests** always go through `core/http_client.py`
4. **Credentials** go in `core/config.py` and `.env.example`
5. **Documentation** goes in `docs/` — not inlined in README

See [docs/extending.md](./docs/extending.md) for a step-by-step guide.

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.
