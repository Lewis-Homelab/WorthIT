#!/usr/bin/env bash
# Deploy script — pull (optional), compose up, health check, automatic rollback.
# Used by:
#   - GitHub Actions (git pull in ci-cd.yml, then DEPLOY_PULL=0 ./scripts/deploy.sh)
#   - Manual server deploys (git pull first, or DEPLOY_PULL=1 ./scripts/deploy.sh)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/load-env.sh"
load_app_env "${ROOT_DIR}"

COMPOSE_ENV=(--env-file "${ROOT_DIR}/config.env")
[[ -f "${ROOT_DIR}/.env" ]] && COMPOSE_ENV+=(--env-file "${ROOT_DIR}/.env")

COMPOSE_FILES=(-f compose.yaml)
if [[ -f compose.prod.yaml ]]; then
  COMPOSE_FILES+=(-f compose.prod.yaml)
fi

run_deploy() {
  local label="$1"
  mkdir -p /home/lewis/homelab/data/WorthIT/postgres
  echo "Starting containers (${label})..."
  docker compose "${COMPOSE_ENV[@]}" "${COMPOSE_FILES[@]}" up -d --build

  echo "Waiting for health check (${label}) at ${HEALTH_URL}..."
  for i in $(seq 1 30); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
      echo "Health check passed (${label})."
      return 0
    fi
    if [[ "$i" -eq 1 ]]; then
      echo "Health check not ready yet, retrying..."
    fi
    sleep 2
  done

  echo "Health check failed (${label})." >&2
  return 1
}

PREVIOUS_COMMIT=$(git rev-parse HEAD)

if [[ "${DEPLOY_PULL:-0}" == "1" ]]; then
  echo "Syncing latest from origin/${DEPLOY_BRANCH}..."
  git fetch origin "${DEPLOY_BRANCH}"
  git reset --hard "origin/${DEPLOY_BRANCH}"
  git clean -fd
fi

if run_deploy "deploy"; then
  exit 0
fi

echo "Deploy failed — rolling back to ${PREVIOUS_COMMIT}..."
git reset --hard "${PREVIOUS_COMMIT}"

if run_deploy "rollback"; then
  echo "Rollback successful — previous version restored." >&2
else
  echo "Rollback failed — manual intervention required." >&2
fi

exit 1
