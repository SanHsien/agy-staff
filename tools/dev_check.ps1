[CmdletBinding()]
param(
    [switch]$Quick
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:NODE_NO_WARNINGS = "1"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==> Checking Pi skills consistency (npm run check:pi)"
npm run check:pi
if ($LASTEXITCODE -ne 0) {
    throw "check:pi failed with exit code $LASTEXITCODE"
}

if ($Quick) {
    Write-Host "==> Quick test pass (focused Windows and Pi packaging tests)"
    node --test --test-timeout=60000 tests/windows.test.mjs tests/pi-packaging.test.mjs
    if ($LASTEXITCODE -ne 0) {
        throw "Quick test suite failed with exit code $LASTEXITCODE"
    }
} else {
    Write-Host "==> Full test suite (node --test --test-timeout=60000 --test-concurrency=1 tests/*.test.mjs)"
    node --test --test-timeout=60000 --test-concurrency=1 tests/*.test.mjs
    if ($LASTEXITCODE -ne 0) {
        throw "Test suite failed with exit code $LASTEXITCODE"
    }
}

Write-Host "==> Compiling Python tools"
python -m compileall -q tools
if ($LASTEXITCODE -ne 0) {
    throw "Python compile failed with exit code $LASTEXITCODE"
}

Write-Host "==> Checking fork document links"
python tools/check_links.py
if ($LASTEXITCODE -ne 0) {
    throw "Link check failed with exit code $LASTEXITCODE"
}

Write-Host "==> Checking upstream updates"
python tools/check_upstream_updates.py --strict
if ($LASTEXITCODE -ne 0) {
    throw "Upstream check failed with exit code $LASTEXITCODE"
}

Write-Host "WINDOWS DEV CHECK GREEN"
