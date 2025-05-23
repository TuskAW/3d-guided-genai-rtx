#!/bin/bash

# Get the NGC API key from the environment variable
#echo "Using NGC API Key: $NGC_API_KEY"

# Ensure NGC_API_KEY is set before running podman
if [ -z "$NGC_API_KEY" ]; then
  echo "NGC API Key is missing!"
  exit 1
fi

# Login to nvcr.io
echo "$NGC_API_KEY" | podman login nvcr.io -u '$oauthtoken' --password-stdin

# Export env vars
export LOCAL_NIM_CACHE=~/.cache/nim

# Setup cache dir
mkdir -p "$LOCAL_NIM_CACHE"
chmod 777 $LOCAL_NIM_CACHE

# Run container
podman run --name FLUX_DEPTH -it --rm \
    --device nvidia.com/gpu=all \
    --shm-size=16GB \
    -e NGC_API_KEY=$NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE:/opt/nim/.cache" \
    -e NIM_RELAX_MEM_CONSTRAINTS=1 \
    -e NIM_OFFLOADING_POLICY=system_ram \
    -e NIM_MODEL_VARIANT=depth \
    -e HF_TOKEN=$hftoken \
    -u $(id -u) \
    -p 8000:8000 \
    nvcr.io/nim/black-forest-labs/flux.1-dev:1.0.0
