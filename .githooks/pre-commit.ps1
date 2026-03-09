# ──────────────────────────────────────────────────────
# Genfluence – Git pre-commit hook (PowerShell version)
# Called by .githooks/pre-commit on Windows when bash is not available.
# ──────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🧪 Running test suite before commit…" -ForegroundColor Cyan
Write-Host "──────────────────────────────────────"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Find python WITH pytest.  Priority: venv first, then system.
$py = $null
$candidates = @(
    (Join-Path $RepoRoot ".." ".venv" "Scripts" "python.exe"),
    (Join-Path $RepoRoot ".venv" "Scripts" "python.exe")
)
foreach ($c in $candidates) {
    if (Test-Path $c) { $py = (Resolve-Path $c).Path; break }
}
if (-not $py) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        # Only use system python if it has pytest
        $check = & python -c "import pytest" 2>&1
        if ($LASTEXITCODE -eq 0) { $py = "python" }
    }
}
if (-not $py) {
    Write-Host "❌ Could not find Python with pytest. Skipping tests." -ForegroundColor Yellow
    exit 0
}

Push-Location $RepoRoot
try {
    & $py -m pytest tests/ -q --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Tests failed — commit BLOCKED." -ForegroundColor Red
        Write-Host "   Fix the failing tests then try again."
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "✅ All tests passed — committing." -ForegroundColor Green
exit 0
