#!/bin/bash
set -e
pip install -r backend/requirements.txt
mkdir -p backend/models
exec gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120