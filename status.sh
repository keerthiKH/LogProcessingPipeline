#!/bin/bash

# Configuration
POD_NAME="log-processing-pod"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Log Processing Pipeline Status ===${NC}"
echo ""

# Check if pod exists
if ! podman pod exists $POD_NAME; then
    echo "Pod '$POD_NAME' is not running."
    exit 0
fi

echo "Pod Status:"
podman pod ps --filter name=$POD_NAME
echo ""

echo "Container Status:"
podman ps --filter pod=$POD_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo -e "${YELLOW}=== Recent Consumer Logs ===${NC}"
podman logs --tail 20 log-consumer
echo ""

echo -e "${YELLOW}=== Recent Producer Logs ===${NC}"
podman logs --tail 20 log-producer
