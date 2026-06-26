#!/bin/sh
# Dev container entrypoint — ensure node_modules is complete before starting Next.js.
# The named Docker volume can be empty or stale; npm install fixes "next: not found".

set -e
cd /app

if [ ! -x node_modules/.bin/next ]; then
  echo "Installing frontend dependencies (node_modules volume missing or incomplete)..."
  npm install
fi

exec npm run dev
