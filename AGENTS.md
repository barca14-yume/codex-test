# Repository Guidelines

Python-first guidance for contributing to this repository. Keep changes small, documented, and tested.

## Project Structure & Module Organization
- Root: project config (e.g., `.editorconfig`, `pyproject.toml`, CI).
- `src/`: Python packages/modules by feature or domain.
- `tests/`: mirrors `src/` layout (e.g., `tests/feature/test_api.py`).
- `docs/`: short design notes and runbooks.
- `.github/`: PR/issue templates and workflows.

Example layout:
```
src/
  app/
    __init__.py
    service.py
tests/
  app/
    test_service.py
```

## Build, Test, and Development Commands
- Install deps: `uv sync` (preferred) or `pip install -r requirements.txt`.
- Run locally: `python -m src.<package>`.
- Tests: `pytest -q`.
- Lint: `ruff check .`.
- Format: `ruff format .` (preferred) and `black --check .` in CI.
Document new commands in `README.md`.

## Coding Style & Naming Conventions
- Style: ruff + black; import sorting via ruff (isort rules).
- Indentation: 4 spaces; line length 100.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes, constants `UPPER_SNAKE_CASE`.
- Imports: prefer absolute from top-level package; stdlib/third-party/first-party groups (ruff enforces).

## Testing Guidelines
- Framework: pytest.
- Structure: tests mirror `src/` paths under `tests/`.
- Naming: files `test_*.py`; functions `test_*`.
- Coverage: target ≥85% for changed code; include error paths and boundary cases.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (e.g., `feat: add user lookup`).
- PRs: clear description, linked issues (`Closes #123`), and test notes; screenshots for UI.
- Checks: ruff, black check, and pytest must pass; keep diffs focused.

## Security & Configuration Tips
- Don’t commit secrets; use `.env` and `.gitignore`.
- Validate inputs at boundaries; avoid logging sensitive data.
- Pin dependencies where appropriate; document migrations in `docs/`.

