#!/bin/bash
set -e

# Configuration
POD_NAME="log-processing-pod"
NETWORK_NAME="log-network"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Building Log Processing Pipeline ===${NC}"

# Build producer image
echo -e "${YELLOW}Building producer image...${NC}"
cd producer
podman build -t log-producer:latest .
cd ..

# Build consumer image
echo -e "${YELLOW}Building consumer image...${NC}"
cd consumer
podman build -t log-consumer:latest .
cd ..

echo -e "${GREEN}✓ All images built successfully${NC}"
echo ""
echo "Images created:"
podman images | grep -E "log-producer|log-consumer"
