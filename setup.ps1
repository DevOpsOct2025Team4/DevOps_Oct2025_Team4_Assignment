Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Command {
  param([string]$Name)
  return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command "node")) {
  Write-Error "Node.js not found. Install Node.js 18+ and rerun this script."
  exit 1
}

if (-not (Test-Command "pnpm")) {
  if (Test-Command "corepack") {
    Write-Host "pnpm not found. Enabling pnpm via corepack..."
    corepack enable | Out-Null
    corepack prepare pnpm@latest --activate | Out-Null
  } else {
    Write-Error "pnpm not found and corepack is unavailable. Install pnpm: npm i -g pnpm"
    exit 1
  }
}

Set-Location $PSScriptRoot

Write-Host "Using root: $PSScriptRoot"
node -v
pnpm -v

pnpm install

$serverEnv     = Join-Path $PSScriptRoot "server\.env"
$serverExample = Join-Path $PSScriptRoot "server\.env.example"
if (-not (Test-Path $serverEnv -PathType Leaf) -and (Test-Path $serverExample -PathType Leaf)) {
  Copy-Item $serverExample $serverEnv -Force
  Write-Host "Created server\.env from server\.env.example"
}

$clientEnv     = Join-Path $PSScriptRoot "client\.env"
$clientExample = Join-Path $PSScriptRoot "client\.env.example"
if (-not (Test-Path $clientEnv -PathType Leaf) -and (Test-Path $clientExample -PathType Leaf)) {
  Copy-Item $clientExample $clientEnv -Force
  Write-Host "Created client\.env from client\.env.example"
}

pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files

Write-Host "Setup complete. Run: pnpm dev"
