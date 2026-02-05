param(
  [string]$Namespace = "devops-assignment",
  [string]$K8sDir = "k8s",
  [string]$Registry = "",
  [string]$Tag = "latest",
  [string]$BackendImage = "",
  [string]$FrontendImage = "",
  [string]$EnvFile = "server/.env"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing dependency: $cmd"
  }
}

function Get-EnvValuesFromFile([string]$path, [string[]]$keys) {
  $values = @{}
  if (-not (Test-Path $path)) {
    return $values
  }
  Get-Content $path | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $parts = $line -split "=", 2
    if ($parts.Length -ne 2) { return }
    $key = $parts[0].Trim()
    if ($keys -notcontains $key) { return }
    $value = $parts[1].Trim()
    $value = $value -replace '\s+#.*$', ''
    $value = $value.Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"')) {
      $value = $value.Substring(1, $value.Length - 2)
    }
    $values[$key] = $value
  }
  return $values
}

Require "kubectl"

if (-not $BackendImage) {
  $BackendImage = if ($Registry) { "$Registry/devops-assignment-backend:$Tag" } else { "devops-assignment-backend:$Tag" }
}
if (-not $FrontendImage) {
  $FrontendImage = if ($Registry) { "$Registry/devops-assignment-frontend:$Tag" } else { "devops-assignment-frontend:$Tag" }
}

$existingNs = & kubectl get ns $Namespace --no-headers 2>$null
if (-not $existingNs) {
  & kubectl create namespace $Namespace
}

$secretKeys = @("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_DIRECT")
$secretValues = Get-EnvValuesFromFile $EnvFile $secretKeys
if (-not $secretValues["SUPABASE_URL"]) { $secretValues["SUPABASE_URL"] = $env:SUPABASE_URL }
if (-not $secretValues["SUPABASE_SERVICE_ROLE_KEY"]) { $secretValues["SUPABASE_SERVICE_ROLE_KEY"] = $env:SUPABASE_SERVICE_ROLE_KEY }
if (-not $secretValues["SUPABASE_DIRECT"]) { $secretValues["SUPABASE_DIRECT"] = $env:SUPABASE_DIRECT }

if (-not $secretValues["SUPABASE_URL"] -or -not $secretValues["SUPABASE_SERVICE_ROLE_KEY"]) {
  throw "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing. Provide them in $EnvFile or set environment variables."
}

$secretArgs = @("-n", $Namespace, "create", "secret", "generic", "backend-secret")
foreach ($entry in $secretValues.GetEnumerator()) {
  if ($entry.Value) {
    $secretArgs += "--from-literal=$($entry.Key)=$($entry.Value)"
  }
}
$secretArgs += "--dry-run=client"
$secretArgs += "-o"
$secretArgs += "yaml"

$secretYaml = & kubectl @secretArgs
$secretYaml | kubectl apply -n $Namespace -f -

& kubectl apply -n $Namespace -f $K8sDir

& kubectl -n $Namespace set image deployment/backend backend=$BackendImage
& kubectl -n $Namespace set image deployment/frontend frontend=$FrontendImage

& kubectl -n $Namespace rollout status statefulset/db --timeout=300s
& kubectl -n $Namespace rollout status deployment/backend --timeout=300s
& kubectl -n $Namespace rollout status deployment/frontend --timeout=300s

& kubectl -n $Namespace get pods -o wide
& kubectl -n $Namespace get svc

Write-Host "Deploy complete."
