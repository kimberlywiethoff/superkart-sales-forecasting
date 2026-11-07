#!/usr/bin/env bash
set -e

NETWORK=superkart-net

# Shared network so the frontend can reach the backend by container name
docker network inspect $NETWORK >/dev/null 2>&1 || docker network create $NETWORK

# Remove old containers if they exist (makes the script safe to re-run)
docker rm -f superkart-backend superkart-frontend >/dev/null 2>&1 || true

# Backend: Flask + Gunicorn on port 7860
docker build -t superkart-backend ./backend_files
docker run -d --name superkart-backend --network $NETWORK -p 7860:7860 superkart-backend

# Frontend: Streamlit on port 8501
docker build -t superkart-frontend ./frontend_files
docker run -d --name superkart-frontend --network $NETWORK -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 superkart-frontend

docker ps
echo "Backend:  port 7860  |  Frontend: port 8501"
echo "Set both ports to Public in the Codespace PORTS tab to share them."
