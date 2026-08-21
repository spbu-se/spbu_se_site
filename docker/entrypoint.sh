#!/bin/sh
set -e

cd /app

# Self-healing schema on boot (idempotent). ensure_schema() initializes a fresh
# DB from the models and repairs an existing one (backup + create_all + column
# diff) — no ops pre-flight needed. Ops can opt out with SE_AUTO_MIGRATE=0 and
# run `python flask_se.py migrate` manually instead.
if [ "${SE_AUTO_MIGRATE:-1}" = "1" ]; then
    echo "[entrypoint] Ensuring schema (SE_AUTO_MIGRATE=0 to opt out)..."
    python flask_se.py migrate
fi

exec "$@"
