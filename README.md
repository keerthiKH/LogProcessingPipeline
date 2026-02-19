# Log Processing Pipeline

A tiny log processing pipeline running in a single Podman pod with three containers communicating over HTTP and RabbitMQ.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Podman Pod                            │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ Log Producer │───▶│   RabbitMQ   │───▶│ Consumer  │ │
│  │  (Flask API) │    │   (Queue)    │    │  (Worker) │ │
│  │  Port: 8080  │    │              │    │           │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         ▲                                       │        │
│         │                                       ▼        │
│    HTTP POST                              /logs/*.txt   │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Log Producer
- **Technology**: Python + Flask
- **Purpose**: HTTP API endpoint that accepts JSON log messages
- **Endpoint**: `POST /log`
- **Port**: 8080 (exposed to host)
- **Function**: Receives logs via HTTP and pushes them to RabbitMQ queue

### 2. Log Queue
- **Technology**: RabbitMQ
- **Purpose**: Message queue for log buffering
- **Queue Name**: `logs`
- **Management UI**: Port 15672 (credentials: guest/guest)

### 3. Log Consumer
- **Technology**: Python
- **Purpose**: Processes logs from queue
- **Function**: Reads from RabbitMQ and writes to `/logs/processed_logs.txt`

## Prerequisites

- Podman installed on your system
- `curl` and `jq` (for testing scripts)
- bash shell

### Installing Podman

**macOS**:
```bash
brew install podman
podman machine init
podman machine start
```

**Linux**:
```bash
# Ubuntu/Debian
sudo apt-get install podman

# Fedora
sudo dnf install podman

# RHEL/CentOS
sudo yum install podman
```

## Quick Start

### 1. Build the containers
```bash
chmod +x *.sh
./build.sh
```

### 2. Start the pipeline
```bash
./start.sh
```

### 3. Send test logs
```bash
./test.sh 10  # Sends 10 test log messages
```

### 4. View processed logs
```bash
./view-logs.sh
```

### 5. Check status
```bash
./status.sh
```

### 6. Stop the pipeline
```bash
./stop.sh
```

## Manual Testing

### Send a single log message
```bash
curl -X POST http://localhost:8080/log \
     -H 'Content-Type: application/json' \
     -d '{
       "level": "INFO",
       "message": "Application started successfully",
       "source": "my-app",
       "user_id": 12345
     }'
```

### Health check
```bash
curl http://localhost:8080/health
```

### View RabbitMQ Management UI
Open in browser: http://localhost:15672
- Username: `guest`
- Password: `guest`

## Log Format

### Input (JSON to Producer)
```json
{
  "level": "INFO",
  "message": "Your log message",
  "source": "application-name",
  "custom_field": "any value"
}
```

### Output (Processed Log File)
```
[2026-02-17T10:30:45.123456] [INFO] Your log message
[2026-02-17T10:30:46.234567] [ERROR] Error occurred
```

## Project Structure

```
logProcessingPipeline/
├── producer/
│   ├── app.py              # Flask application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Container image definition
├── consumer/
│   ├── app.py              # Consumer worker
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Container image definition
├── build.sh                # Build all container images
├── start.sh                # Start the pod and all containers
├── stop.sh                 # Stop and remove the pod
├── status.sh               # Check pod and container status
├── test.sh                 # Send test log messages
├── view-logs.sh            # View processed logs
└── README.md               # This file
```

## Environment Variables

### Producer
- `RABBITMQ_HOST`: RabbitMQ hostname (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_QUEUE`: Queue name (default: logs)
- `PORT`: HTTP server port (default: 8080)

### Consumer
- `RABBITMQ_HOST`: RabbitMQ hostname (default: localhost)
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_QUEUE`: Queue name (default: logs)
- `LOG_FILE`: Output log file path (default: /logs/processed_logs.txt)

## Troubleshooting

### Check container logs
```bash
# Producer logs
podman logs log-producer

# Consumer logs
podman logs log-consumer

# RabbitMQ logs
podman logs rabbitmq
```

### Restart a specific container
```bash
podman restart log-producer
podman restart log-consumer
podman restart rabbitmq
```

### Clean up everything
```bash
./stop.sh
podman pod rm -f log-processing-pod
podman volume rm log-data
podman image rm log-producer:latest log-consumer:latest
```

### Common Issues

**Issue**: Consumer can't connect to RabbitMQ
- **Solution**: Wait a few more seconds for RabbitMQ to fully start, or check logs with `podman logs rabbitmq`

**Issue**: Port 8080 already in use
- **Solution**: Edit `start.sh` and change `PRODUCER_PORT` to another port

**Issue**: Permission denied on scripts
- **Solution**: Run `chmod +x *.sh`

## Advanced Usage

### Scale consumers
You can run multiple consumer instances for parallel processing:
```bash
podman run -d \
    --pod log-processing-pod \
    --name log-consumer-2 \
    -e RABBITMQ_HOST=localhost \
    -e RABBITMQ_PORT=5672 \
    -v log-data:/logs \
    log-consumer:latest
```

### Custom log output location
Modify the consumer's `LOG_FILE` environment variable:
```bash
-e LOG_FILE=/logs/custom-output.log
```

### Persist logs on host
Mount a host directory instead of using a volume:
```bash
-v /path/on/host:/logs
```

## Why Podman Pods?

Podman pods are similar to Kubernetes pods - all containers share:
- **Network namespace**: Containers communicate via `localhost`
- **IPC namespace**: Inter-process communication
- **UTS namespace**: Hostname

This makes it perfect for tightly coupled microservices that need to communicate efficiently.

## Next Steps

- Add authentication to the producer API
- Implement log filtering and routing
- Add log aggregation and analytics
- Export logs to external systems (Elasticsearch, S3, etc.)
- Add Prometheus metrics
- Implement log rotation

## License

MIT
