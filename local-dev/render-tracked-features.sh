#!/bin/bash
set -e

if [ $# -lt 1 ]; then
    echo "usage: $0 <dataset_folder> (needs to contain images/ directory)"
    exit 1
fi

dataset_folder="$1"

if [ "${dataset_folder:0:1}" == '-' ]; then
    echo "usage: $0 <dataset_folder> (needs to contain images/ directory)"
    exit 1
fi

if [ ! -d "${dataset_folder}/images" ]; then
    echo "usage: $0 <dataset_folder> (needs to contain images/ directory)"
    exit 1
fi

if [ ! -d "${dataset_folder}" ]
then
    mkdir -p "${dataset_folder}"
fi

if [ ! -d "${dataset_folder}/reports/pano-images/" ]
then
    mkdir -p "${dataset_folder}/reports/pano-images/"
fi

docker run \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u):$(id -g) \
    -v "${dataset_folder}"/:/external/in \
    -it --rm calibration_docker python3 /source/OpenSfM/bin/render_features.py --dataset /external/in/ --images
