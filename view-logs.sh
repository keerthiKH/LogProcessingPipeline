#!/bin/bash

# View processed logs from the consumer

echo "=== Processed Logs ==="
podman exec log-consumer cat /logs/processed_logs.txt 2>/dev/null || echo "No logs found yet or consumer not running"
