#!/bin/bash

# Configuration
POD_NAME="log-processing-pod"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Stopping Log Processing Pipeline ===${NC}"

# Check if pod exists
if ! podman pod exists $POD_NAME; then
    echo "Pod '$POD_NAME' does not exist."
    exit 0
fi

# Stop and remove the pod (this also stops all containers in it)
echo -e "${YELLOW}Stopping and removing pod '$POD_NAME'...${NC}"
podman pod stop $POD_NAME
podman pod rm $POD_NAME

echo -e "${GREEN}✓ Pod stopped and removed successfully${NC}"
