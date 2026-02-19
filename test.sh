#!/bin/bash

# Configuration
PRODUCER_PORT=8080
NUM_LOGS=${1:-5}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Sending $NUM_LOGS test log messages ===${NC}"

for i in $(seq 1 $NUM_LOGS); do
    LEVEL=$([ $((i % 3)) -eq 0 ] && echo "ERROR" || [ $((i % 2)) -eq 0 ] && echo "WARN" || echo "INFO")
    
    curl -X POST http://localhost:$PRODUCER_PORT/log \
         -H 'Content-Type: application/json' \
         -d "{\"level\": \"$LEVEL\", \"message\": \"Test log message #$i\", \"source\": \"test-script\"}" \
         -s | jq .
    
    echo ""
    sleep 0.5
done

echo -e "${GREEN}✓ Sent $NUM_LOGS log messages${NC}"
echo ""
echo "To view processed logs:"
echo "  podman exec log-consumer cat /logs/processed_logs.txt"
