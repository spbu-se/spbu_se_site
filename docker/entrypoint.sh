#!/bin/sh
set -e

cd /app

# Initialize the SQLite database (idempotent) before serving requests.
if [ ! -f databases/se.db ]; then
    echo "[entrypoint] Initializing database..."
    python flask_se.py init
fi

exec "$@"
