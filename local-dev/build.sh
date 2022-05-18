#!/bin/bash
set -e
docker build -f Dockerfile.local -t calibration_docker .
