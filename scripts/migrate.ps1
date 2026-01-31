Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Command {
  param([string]$Name)
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "docker")) {
  Write-Error "Docker not found. Install Docker Desktop and rerun this script."
  exit 1
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$message = "auto-$timestamp"

Write-Host "Generating migration: $message"
docker compose run --rm -v "$root:/app" -w /app/server server `
  alembic -c /app/server/alembic.ini revision --autogenerate -m "$message"

Write-Host "Applying migrations..."
docker compose run --rm -v "$root:/app" -w /app/server server `
  alembic -c /app/server/alembic.ini upgrade head
