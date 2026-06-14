#!/usr/bin/env bash
# Load project configuration for shell scripts and Docker Compose.
#
# Load order (later overrides earlier):
#   1. config.env  — committed, shared config (ports, paths, names)
#   2. .env        — optional, gitignored (secrets and local overrides)

load_app_env() {
  local root="${1:-.}"

  set -a
  if [[ -f "${root}/config.env" ]]; then
    # shellcheck disable=SC1091
    source "${root}/config.env"
  fi
  if [[ -f "${root}/.env" ]]; then
    # shellcheck disable=SC1091
    source "${root}/.env"
  fi
  set +a

  : "${APP_NAME:=hello-homelab}"
  : "${APP_PORT:=5001}"
  : "${HOST_PORT:=5050}"
  : "${HEALTH_PATH:=/health}"
  : "${DEPLOY_BRANCH:=main}"

  export APP_NAME APP_PORT HOST_PORT HEALTH_PATH DEPLOY_BRANCH
  export WEB_HOST_PORT="${WEB_HOST_PORT:-3000}"
  export HEALTH_URL="${HEALTH_URL:-http://localhost:${HOST_PORT}${HEALTH_PATH}}"
}
