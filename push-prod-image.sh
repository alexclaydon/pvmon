#!/bin/bash

# Build a production container image and push it to a registry

echo "Building Docker image and pushing to GitHub Container Registry (GHCR)" && sleep 1

currentDate=$(date -I)

docker image build -t pvmon:"$currentDate" . || { echo "Docker operation failed"; exit 1; }

docker tag pvmon:"$currentDate" ghcr.io/alexclaydon/pvmon:"$currentDate"

docker push ghcr.io/alexclaydon/pvmon:"$currentDate"

echo "Custom container successfully pushed to GHCR"