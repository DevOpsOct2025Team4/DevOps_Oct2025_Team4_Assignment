param(
  [string]$BaseUrl = "",
  [string]$Username = "",
  [string]$Password = "",
  [string]$Browser = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $root ".env"

if (Test-Path $envFile) {
  Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $parts = $line -split "=", 2
    if ($parts.Length -ne 2) { return }
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()
    $value = $value -replace '\s+#.*$', ''
    $value = $value.Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
      $value = $value.Substring(1, $value.Length - 2)
    }
    if ($key -and -not (Get-Item "Env:$key" -ErrorAction SilentlyContinue)) {
      Set-Item -Path "Env:$key" -Value $value
    }
  }
}

if (-not $env:ROBOT_BASE_URL) {
  $env:ROBOT_BASE_URL = "http://localhost:5173"
}

if ($BaseUrl) { $env:ROBOT_BASE_URL = $BaseUrl }
if ($Username) { $env:ROBOT_USERNAME = $Username }
if ($Password) { $env:ROBOT_PASSWORD = $Password }
if ($Browser) { $env:ROBOT_BROWSER = $Browser }

Write-Host "Running Robot tests against $env:ROBOT_BASE_URL"
if (-not $env:ROBOT_USERNAME -or -not $env:ROBOT_PASSWORD) {
  Write-Host "ROBOT_USERNAME/ROBOT_PASSWORD not set - login test will be skipped."
}

robot -d robot/results robot/tests/frontend_smoke.robot
