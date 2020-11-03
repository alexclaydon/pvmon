#!/bin/bash

# Build a production container image and push it to a registry

echo "Building Docker image and pushing to GitHub Container Registry (GHCR)" && sleep 1

docker image build -t pvmon:latest . || { echo "Docker operation failed"; exit 1; }

docker tag pvmon:latest ghcr.io/alexclaydon/pvmon:latest

docker push ghcr.io/alexclaydon/pvmon:latest

echo "Custom container successfully pushed to GHCR"