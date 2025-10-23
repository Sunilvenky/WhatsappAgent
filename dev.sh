#!/usr/bin/env bash
# Dev helper to run docker-compose and run migrations/seeds
set -euo pipefail
CMD=${1:-up}

if [ "$CMD" = "up" ]; then
  docker-compose -f infra/docker-compose.yml up -d --build
  echo "Waiting for services to become healthy..."
  sleep 3
  echo "(Stub) Running migrations..."
  # In future: run alembic migrations here
  exit 0
fi

if [ "$CMD" = "down" ]; then
  docker-compose -f infra/docker-compose.yml down
  exit 0
fi

echo "Usage: $0 [up|down]"