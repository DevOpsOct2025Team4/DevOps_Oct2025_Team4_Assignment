#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-devops-assignment}"
K8S_DIR="${K8S_DIR:-k8s}"
BACKEND_IMAGE="${BACKEND_IMAGE:-devops-assignment-backend:local}"
FRONTEND_IMAGE="${FRONTEND_IMAGE:-devops-assignment-frontend:local}"
VITE_API_BASE_URL="${VITE_API_BASE_URL:-/api}"

require() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing dependency: $1" >&2
    exit 1
  }
}

require docker
require kubectl
require kind

if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  kind create cluster --name "${CLUSTER_NAME}"
fi

Dockerfile_root="$(pwd)"

docker build -t "$BACKEND_IMAGE" -f server/Dockerfile "$Dockerfile_root"
docker build -t "$FRONTEND_IMAGE" -f client/Dockerfile --build-arg VITE_API_BASE_URL="$VITE_API_BASE_URL" "$Dockerfile_root"

kind load docker-image "$BACKEND_IMAGE" --name "$CLUSTER_NAME"
kind load docker-image "$FRONTEND_IMAGE" --name "$CLUSTER_NAME"

ENV_FILE="server/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ -z "${SUPABASE_URL:-}" || -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
  echo "SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing in server/.env. Update server/.env, then re-run." >&2
  exit 1
fi

kubectl create secret generic backend-secret \
  --from-literal=SUPABASE_URL="${SUPABASE_URL}" \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}" \
  --from-literal=SUPABASE_DIRECT="${SUPABASE_DIRECT:-}" \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f "$K8S_DIR"

kubectl rollout restart deployment/backend >/dev/null 2>&1 || true

kubectl rollout status statefulset/db --timeout=180s
kubectl rollout status deployment/backend --timeout=180s
kubectl rollout status deployment/frontend --timeout=180s

kubectl get pods -o wide
kubectl get svc

echo "Verifying backend health from inside cluster..."
kubectl run k8s-healthcheck --rm -i --restart=Never \
  --image=curlimages/curl:8.7.1 \
  --command -- sh -c "curl -sf http://backend:5000/api/health && echo OK"

echo "Local access (new terminal):"
echo "  kubectl port-forward svc/frontend 5173:80"
echo "  kubectl port-forward svc/backend 5000:5000"
