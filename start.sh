#!/bin/bash
set -e

# Configuration
POD_NAME="log-processing-pod"
PRODUCER_PORT=8080

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Starting Log Processing Pipeline ===${NC}"

# Check if pod already exists
if podman pod exists $POD_NAME; then
    echo -e "${RED}Pod '$POD_NAME' already exists. Please run stop.sh first.${NC}"
    exit 1
fi

# Create pod with port mapping
echo -e "${YELLOW}Creating pod '$POD_NAME'...${NC}"
podman pod create \
    --name $POD_NAME \
    -p $PRODUCER_PORT:8080

# Start RabbitMQ
echo -e "${YELLOW}Starting RabbitMQ container...${NC}"
podman run -d \
    --pod $POD_NAME \
    --name rabbitmq \
    -e RABBITMQ_DEFAULT_USER=guest \
    -e RABBITMQ_DEFAULT_PASS=guest \
    docker.io/rabbitmq:3-management

# Wait for RabbitMQ to be ready
echo -e "${YELLOW}Waiting for RabbitMQ to be ready...${NC}"
sleep 10

# Start consumer
echo -e "${YELLOW}Starting log consumer...${NC}"
podman run -d \
    --pod $POD_NAME \
    --name log-consumer \
    -e RABBITMQ_HOST=localhost \
    -e RABBITMQ_PORT=5672 \
    -e RABBITMQ_QUEUE=logs \
    -e LOG_FILE=/logs/processed_logs.txt \
    -v log-data:/logs \
    log-consumer:latest

# Start producer
echo -e "${YELLOW}Starting log producer...${NC}"
podman run -d \
    --pod $POD_NAME \
    --name log-producer \
    -e RABBITMQ_HOST=localhost \
    -e RABBITMQ_PORT=5672 \
    -e RABBITMQ_QUEUE=logs \
    -e PORT=8080 \
    log-producer:latest

echo -e "${GREEN}✓ All containers started successfully${NC}"
echo ""
echo "Pod Status:"
podman pod ps --filter name=$POD_NAME
echo ""
echo "Container Status:"
podman ps --filter pod=$POD_NAME
echo ""
echo -e "${GREEN}Producer API available at: http://localhost:$PRODUCER_PORT${NC}"
echo -e "${GREEN}RabbitMQ Management UI available at: http://localhost:15672${NC}"
echo -e "  Username: guest"
echo -e "  Password: guest"
echo ""
echo "To send a test log:"
echo "  curl -X POST http://localhost:$PRODUCER_PORT/log \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"level\": \"INFO\", \"message\": \"Test log message\"}'"
