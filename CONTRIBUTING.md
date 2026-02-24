# Contributing to Social Media SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

---

## Reporting Issues

1. Check existing issues to avoid duplicates.
2. Use a clear, descriptive title.
3. Include:
   - Python version
   - OS and version
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant log output (mask any credentials)

---

## Pull Request Process

### 1. Fork and Clone

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

- **Python 3.10+**: Use modern type hints (`str | None`).
- **PEP 8**: Follow standard Python style conventions.
- **Type Hints**: All function signatures must have complete type annotations.
- **Docstrings**: Use clear descriptions for all public methods.
- **Logging**: Use `loguru.logger` instead of `print()`.
- **No Raw HTTP**: All requests must go through `AsyncHttpClient`.

### 4. Commit Messages

Use clear and consistent commit messages:

- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `refactor`: Code restructuring

### 5. Submit Your PR

- Push your branch and open a Pull Request.
- Provide a clear description of your changes.
- Ensure existing functionality still works.
- Add documentation for new features.

---

## Architecture Guidelines

1. **Platform Clients**: Inherit `BasePlatformClient` and implement `get_profile()` and `get_all_content()`.
2. **Data Models**: Use Pydantic models for data normalization.
3. **HTTP Requests**: Always route through `core/http_client.py`.
4. **Credentials**: Add to `core/config.py` and `.env.example`.
5. **Documentation**: Place new guides in the `docs/` directory.

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
