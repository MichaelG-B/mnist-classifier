#!/bin/bash
# OWNER: Person A. Run on the AWS machine:  ./deploy.sh
set -e

cd ~/mnist-classifier
echo ">>> Pulling latest code"
git pull origin main

echo ">>> Stopping old container (ignore errors if none running)"
docker stop site 2>/dev/null || true
docker rm site 2>/dev/null || true

echo ">>> Building image (5-15 min on a small instance)"
docker build -t mnist-site .

echo ">>> Starting container"
docker run -d -p 8000:8000 --restart unless-stopped --name site mnist-site

sleep 3
docker ps
echo ""
echo ">>> Deployed. Check the tunnel is alive:  tmux attach -t tunnel"
