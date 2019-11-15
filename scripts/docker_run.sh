#!/usr/bin/env bash
docker image build -t dcgan . && \
docker run -it --rm --gpus all -v "/home/40057686/datasets:/datasets" -v "/home/40057686/results:/results" dcgan bash