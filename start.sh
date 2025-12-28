#!/usr/bin/env bash
set -e

echo "Starting LTrail backend..."

cd backend || exit 1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python -m uvicorn main:app --host 0.0.0.0 --port $PORT
