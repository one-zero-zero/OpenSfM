#!/bin/bash
set -e

if [ $# -lt 1 ]; then
    echo 'usage: $0 <dataset_folder> (needs to contain images/ directory)'
    exit 1
fi

dataset_folder="$1"

if [ "${dataset_folder:0:1}" == '-' ]; then
    echo 'usage: $0 <dataset_folder> (needs to contain images/ directory)'
    exit 1
fi

if [ ! -d "${dataset_folder}/images" ]; then
    echo 'usage: $0 <dataset_folder> (needs to contain images/ directory)'
    exit 1
fi

if [ ! -d ${dataset_folder} ]
then
    mkdir -p "${dataset_folder}"
fi

docker run \
    -v /etc/passwd:/etc/passwd:ro -v /etc/group:/etc/group:ro --user $(id -u):$(id -g) \
    -v "${dataset_folder}"/:/external/in \
    -it --rm calibration_docker bash
