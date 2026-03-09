# ──────────────────────────────────────────────────
# Setup script – configures git to use .githooks/
# Run once after cloning:   .\setup-hooks.ps1
# ──────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

Push-Location $PSScriptRoot
try {
    Write-Host "🔧 Configuring git to use .githooks/ directory…" -ForegroundColor Cyan
    git config core.hooksPath .githooks

    Write-Host "✅ Done! The pre-commit hook will now run tests before every commit." -ForegroundColor Green
    Write-Host "   To skip tests for a WIP commit:  git commit --no-verify"
} finally {
    Pop-Location
}
