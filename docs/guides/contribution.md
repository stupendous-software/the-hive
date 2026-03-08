# Contributing Guide

We welcome contributions to Agent Zero! This guide helps you get started.

## Quick Start

1. Fork the repository on GitHub.
2. Clone your fork locally.
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r a0/requirements.txt
   pip install -r a0/requirements-dev.txt  # if present
   ```
4. Install pre-commit hooks (optional):
   ```bash
   pre-commit install
   ```

## Workflow

- `git checkout -b feature/AmazingFeature`
- Make changes and write/add tests.
- Run tests: `pytest tests/`
- Format code: `black . && isort .`
- Commit with clear message: `git commit -m "Add AmazingFeature"`
- Push and open a Pull Request.

## Code Style

PEP 8 compliant. Use Black and isort.

## Testing

- Unit tests in `tests/`.
- For new tools, include unit and integration tests.
- Screenshots or logs are helpful for UI changes.

## Documentation

- Update relevant files in `docs/`.
- Add docstrings to public functions/classes.
- Readme updates for major features.

## Areas We Need Help With

- New skills and tool integrations
- Performance optimizations
- Security hardening
- Translations and localization
- Better error messages and diagnostics
- Observability enhancements

## Community

Join our Discord for dev chat and support.

## License

Contributions are licensed under the MIT License.

Thank you for making Agent Zero better! 🚀
