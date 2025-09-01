# Repository

[![CI](https://github.com/barca14-yume/codex-test/actions/workflows/ci.yml/badge.svg)](https://github.com/barca14-yume/codex-test/actions/workflows/ci.yml)

## Python-first Configuration

This repository is configured for Python development with a lightweight, tools-first setup:

- CI: GitHub Actions (`.github/workflows/ci.yml`) runs on push/PR using Python 3.11. It installs deps via `uv` (falls back to `pip`), then runs `ruff check .`, `black --check .`, and `pytest -q --cov=src --cov-report=xml`.
- Tooling: `ruff` (lint + isort), `black` (format), `pytest` (tests). Minimal defaults live in `pyproject.toml`.
- Structure: put code in `src/` and mirror it in `tests/` (e.g., `src/app/service.py` → `tests/app/test_service.py`). Aim for ≥85% coverage on changed code.

Local quickstart:
- Install deps: `uv sync` (if using uv) or `pip install -r requirements.txt`
- Lint: `ruff check .`
- Format: `ruff format .` (and ensure `black --check .` passes)
- Test: `pytest -q`

See `AGENTS.md` for contributor guidelines.

## CLI Usage

Local run without install:
- `python -m src.app.sales_cli docs/samples/sales.csv --top 2 --by-date --out out.csv`

Installed entry point (after `uv pip install -e .` or `pip install -e .`):
- `sales-cli docs/samples/sales.csv --top 2 --by-date --out out.csv`
