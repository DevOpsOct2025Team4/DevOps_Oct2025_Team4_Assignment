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
$versionsDir = Join-Path $root "server/alembic/versions"

Write-Host "Generating migration: $message"
$before = @(Get-ChildItem -Path $versionsDir -Filter "*.py" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
docker compose run --rm -v "${root}:/app" -w /app/server server `
  alembic -c /app/server/alembic.ini revision --autogenerate -m "$message"
$after = @(Get-ChildItem -Path $versionsDir -Filter "*.py" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
$newFiles = @(
  Compare-Object $before $after |
    Where-Object { $_.SideIndicator -eq "=>" } |
    ForEach-Object { $_.InputObject }
)

if ($newFiles.Count -eq 0) {
  Write-Host "No new migration file created."
} else {
  foreach ($file in $newFiles) {
    $content = Get-Content -Path $file -Raw
    if ($content -match "def upgrade\(\):\s*\r?\n\s*pass" -and $content -match "def downgrade\(\):\s*\r?\n\s*pass") {
      Write-Host "No schema changes detected. Removing empty migration: $(Split-Path $file -Leaf)"
      Remove-Item -Path $file -Force
    }
  }
}

Write-Host "Applying migrations..."
docker compose run --rm -v "${root}:/app" -w /app/server server `
  alembic -c /app/server/alembic.ini upgrade head
