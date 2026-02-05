param(
  [string]$K8sDir = "k8s",
  [string]$BackendImage = "devops-assignment-backend:local",
  [string]$FrontendImage = "devops-assignment-frontend:local",
  [string]$ViteApiBaseUrl = "/api",
  [int]$FrontendPort = 5174,
  [switch]$PortForward,
  [switch]$UseKind
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require([string]$cmd) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
    throw "Missing dependency: $cmd"
  }
}

Require "docker"
Require "kubectl"
if ($UseKind) {
  Require "kind"
  $ClusterName = "devops-assignment"
  $clusters = & kind get clusters
  if ($clusters -notcontains $ClusterName) {
    & kind create cluster --name $ClusterName
  }
}

$root = (Get-Location).Path

& docker build -t $BackendImage -f server/Dockerfile $root
& docker build -t $FrontendImage -f client/Dockerfile --build-arg "VITE_API_BASE_URL=$ViteApiBaseUrl" $root

if ($UseKind) {
  & kind load docker-image $BackendImage --name $ClusterName
  & kind load docker-image $FrontendImage --name $ClusterName
}

function Get-EnvValuesFromFile([string]$path, [string[]]$keys) {
  $values = @{}
  if (-not (Test-Path $path)) {
    throw "Missing env file: $path"
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

$envFile = Join-Path $root "server\\.env"
$secretKeys = @("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_DIRECT")
$secretValues = Get-EnvValuesFromFile $envFile $secretKeys

if (-not $secretValues.ContainsKey("SUPABASE_URL") -or -not $secretValues.ContainsKey("SUPABASE_SERVICE_ROLE_KEY")) {
  throw "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing in server/.env. Update server/.env, then re-run."
}

$secretArgs = @("create", "secret", "generic", "backend-secret")
foreach ($entry in $secretValues.GetEnumerator()) {
  if ($entry.Value) {
    $secretArgs += "--from-literal=$($entry.Key)=$($entry.Value)"
  }
}
$secretArgs += "--dry-run=client"
$secretArgs += "-o"
$secretArgs += "yaml"

$secretYaml = & kubectl @secretArgs
$secretYaml | kubectl apply -f -

& kubectl apply -f $K8sDir

& kubectl rollout restart deployment/backend | Out-Null

& kubectl rollout status statefulset/db --timeout=180s
& kubectl rollout status deployment/backend --timeout=180s
& kubectl rollout status deployment/frontend --timeout=180s

& kubectl get pods -o wide
& kubectl get svc

Write-Host "Verifying backend health from inside cluster..."
& kubectl run k8s-healthcheck --rm -i --restart=Never `
  --image=curlimages/curl:8.7.1 `
  --command -- sh -c "curl -sf http://backend:5000/api/health && echo OK"

Write-Host "Local access (new terminal):"
Write-Host "  kubectl port-forward svc/frontend $FrontendPort`:80"
Write-Host "  kubectl port-forward svc/backend 5000:5000"

if ($PortForward) {
  Write-Host "Starting port-forward on http://localhost:$FrontendPort ..."
  & kubectl port-forward svc/frontend "$FrontendPort`:80"
}
