#!/usr/bin/env bash
set -e

alembic upgrade head

ls -l /app

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
