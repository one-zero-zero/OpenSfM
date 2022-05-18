#!/bin/bash
set -e

IMAGE=opensfm-local
docker build -f Dockerfile.ceres2 -t $IMAGE .
# docker push $IMAGE
