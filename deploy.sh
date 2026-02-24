#!/usr/bin/env bash
set -euo pipefail

# --- Config ---
PROJECT_ID="gen-lang-client-0754692302"
REGION="us-central1"
BACKEND_SERVICE="mundostra-api"
FRONTEND_SERVICE="mundostra-web"
BACKEND_IMAGE="gcr.io/${PROJECT_ID}/${BACKEND_SERVICE}"
FRONTEND_IMAGE="gcr.io/${PROJECT_ID}/${FRONTEND_SERVICE}"

# Load .env file for secret values
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
else
  echo "ERROR: .env file not found. Create one with required variables."
  exit 1
fi

# Helper: submit a Cloud Build and wait for it to finish
submit_and_wait() {
  local config_file="$1"
  local label="$2"

  # Submit async and capture build ID
  BUILD_ID=$(gcloud builds submit \
    --project="${PROJECT_ID}" \
    --config="${config_file}" \
    --async \
    --format="value(id)" \
    --quiet 2>&1 | tail -1)

  echo "    Build ID: ${BUILD_ID}"
  echo "    Logs: https://console.cloud.google.com/cloud-build/builds/${BUILD_ID}?project=${PROJECT_ID}"
  echo "    Waiting for ${label} build to complete..."

  # Poll until build finishes
  while true; do
    STATUS=$(gcloud builds describe "${BUILD_ID}" \
      --project="${PROJECT_ID}" \
      --format="value(status)" 2>/dev/null || echo "UNKNOWN")

    case "${STATUS}" in
      SUCCESS)
        echo "    ✓ ${label} build succeeded."
        return 0
        ;;
      FAILURE|INTERNAL_ERROR|TIMEOUT|CANCELLED|EXPIRED)
        echo "    ✗ ${label} build failed with status: ${STATUS}"
        exit 1
        ;;
      *)
        sleep 10
        ;;
    esac
  done
}

echo "=== Deploying Mundostra to Cloud Run ==="
echo "Project: ${PROJECT_ID}"
echo "Region:  ${REGION}"
echo ""

# --- Step 1: Build & push backend image ---
echo ">>> Building backend image..."
cat > /tmp/cloudbuild-backend.yaml <<CBEOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.backend', '-t', '${BACKEND_IMAGE}', '.']
images: ['${BACKEND_IMAGE}']
CBEOF
submit_and_wait /tmp/cloudbuild-backend.yaml "Backend"

# --- Step 2: Deploy backend to Cloud Run ---
echo ">>> Deploying backend service..."
gcloud run deploy "${BACKEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${BACKEND_IMAGE}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3 \
  --timeout=300 \
  --set-env-vars="APP_ENV=production" \
  --set-env-vars="MOCK_LLM=${MOCK_LLM:-false}" \
  --set-env-vars="AWS_REGION=${AWS_REGION:-us-east-1}" \
  --set-env-vars="AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-}" \
  --set-env-vars="AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-}" \
  --set-env-vars="GCP_PROJECT_ID=${GCP_PROJECT_ID:-${PROJECT_ID}}" \
  --set-env-vars="GCP_LOCATION=${GCP_LOCATION:-us-central1}" \
  --set-env-vars="OPENAI_API_KEY=${OPENAI_API_KEY:-}" \
  --set-env-vars="GMAIL_ENABLED=${GMAIL_ENABLED:-false}" \
  --set-env-vars="GMAIL_SENDER=${GMAIL_SENDER:-}" \
  --set-env-vars="GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD:-}" \
  --set-env-vars="GMAIL_RECIPIENT=${GMAIL_RECIPIENT:-}" \
  --set-env-vars="AMADEUS_CLIENT_ID=${AMADEUS_CLIENT_ID:-}" \
  --set-env-vars="AMADEUS_CLIENT_SECRET=${AMADEUS_CLIENT_SECRET:-}" \
  --set-env-vars="AMADEUS_ENV=${AMADEUS_ENV:-test}" \
  --quiet

# --- Step 3: Capture backend URL ---
BACKEND_URL=$(gcloud run services describe "${BACKEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(status.url)")

echo ""
echo ">>> Backend deployed at: ${BACKEND_URL}"

# Derive WebSocket URL (wss:// on the same host)
BACKEND_HOST=$(echo "${BACKEND_URL}" | sed 's|https://||')
WS_URL="wss://${BACKEND_HOST}/ws/trace"

# --- Step 4: Build & push frontend image ---
echo ">>> Building frontend image..."
cat > /tmp/cloudbuild-frontend.yaml <<CBEOF
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-f', 'Dockerfile.frontend', '--build-arg', 'NEXT_PUBLIC_API_URL=${BACKEND_URL}', '--build-arg', 'NEXT_PUBLIC_WS_URL=${WS_URL}', '-t', '${FRONTEND_IMAGE}', '.']
images: ['${FRONTEND_IMAGE}']
CBEOF
submit_and_wait /tmp/cloudbuild-frontend.yaml "Frontend"

# --- Step 5: Deploy frontend to Cloud Run ---
echo ">>> Deploying frontend service..."
gcloud run deploy "${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${FRONTEND_IMAGE}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=3000 \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3 \
  --quiet

# --- Step 6: Capture frontend URL ---
FRONTEND_URL=$(gcloud run services describe "${FRONTEND_SERVICE}" \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --format="value(status.url)")

echo ""
echo "==========================================="
echo "  Mundostra deployed successfully!"
echo "==========================================="
echo "  Backend API:  ${BACKEND_URL}"
echo "  Frontend Web: ${FRONTEND_URL}"
echo "  Health Check: ${BACKEND_URL}/health"
echo "  WebSocket:    ${WS_URL}"
echo "==========================================="
