#!/bin/bash

echo "Starting LTrail backend..."

cd backend || exit 1

pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port $PORT
