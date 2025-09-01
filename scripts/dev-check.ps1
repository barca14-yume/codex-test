param([switch]$OpenHtml)

# Dev quick check: lint → format → format-check → tests (XML+HTML coverage)
# If blocked: Set-ExecutionPolicy -Scope Process Bypass -Force

$ErrorActionPreference = "Stop"

Write-Host "==> Ruff check"
ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Ruff format"
ruff format .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Black check"
black --check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Pytest (xml + html coverage)"
# PYTHONPATH は pyproject の pythonpath=["src"] で不要なはずですが、明示しても無害です
$env:PYTHONPATH = "src"
pytest -q --cov=src --cov-report=xml --cov-report=html
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($OpenHtml) {
  Start-Process .\htmlcov\index.html
}

Write-Host "✅ Done"
