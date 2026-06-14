#!/usr/bin/env bash
# Initialize a new project from this template.
# Updates config.env and pyproject.toml — the only files to edit for names/ports.
#
# Usage: ./scripts/init-project.sh <app-name> [host-port]
# Example: ./scripts/init-project.sh my-api 8080

set -euo pipefail

APP_NAME="${1:?Usage: $0 <app-name> [host-port]}"
HOST_PORT="${2:-5050}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

CONFIG_FILE="${ROOT_DIR}/config.env"

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Missing config.env" >&2
  exit 1
fi

sed -i.bak "s/^APP_NAME=.*/APP_NAME=${APP_NAME}/" "$CONFIG_FILE"
sed -i.bak "s/^HOST_PORT=.*/HOST_PORT=${HOST_PORT}/" "$CONFIG_FILE"
sed -i.bak "s|^DEPLOY_PATH=.*|DEPLOY_PATH=/opt/apps/${APP_NAME}|" "$CONFIG_FILE"
rm -f "${CONFIG_FILE}.bak"

if [[ -f pyproject.toml ]]; then
  sed -i.bak "s/^name = .*/name = \"${APP_NAME}\"/" pyproject.toml
  rm -f pyproject.toml.bak
fi

echo "Initialized project: ${APP_NAME}"
echo ""
echo "Updated:"
echo "  config.env     (APP_NAME, HOST_PORT, DEPLOY_PATH)"
echo "  pyproject.toml (name)"
echo ""
echo "Next steps:"
echo "  1. uv sync && make test"
echo "  2. Commit and push config.env"
echo "  3. Clone on server at: /opt/apps/${APP_NAME}"
echo "  4. Set GitHub repo variable DEPLOY_PATH=/opt/apps/${APP_NAME}"
echo "  5. make dev  →  http://localhost:${HOST_PORT}"
