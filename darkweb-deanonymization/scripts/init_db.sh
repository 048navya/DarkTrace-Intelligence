#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
python scripts/init_db.py
