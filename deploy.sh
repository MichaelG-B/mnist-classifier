#!/bin/bash
# OWNER: Person A. Redeploys the site on the Lightsail server.
# Usage on the server:  ~/deploy.sh
set -e

cd ~/mnist-classifier
git pull origin main

sudo docker compose down

# --network=host: the Bitnami image's firewall drops forwarded traffic, so
# containers on Docker's default bridge have no outbound internet and pip
# cannot reach PyPI. Building on the host's network stack sidesteps that.
sudo docker build --network=host -t mnist-classifier-web .

sudo docker compose up -d
sudo docker compose ps
echo "Deployed."
