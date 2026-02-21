#!/usr/bin/env python3
"""
Log Consumer - Reads log messages from RabbitMQ and processes them
"""
import json
import os
import sys
import time
import pika
from datetime import datetime

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'logs')
LOG_FILE = os.getenv('LOG_FILE', '/logs/processed_logs.txt')


def connect_to_rabbitmq():
    """Connect to RabbitMQ with retry logic"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} (attempt {attempt + 1}/{max_retries})")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
            )
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            print("Successfully connected to RabbitMQ")
            return connection, channel
        except Exception as e:
            print(f"Connection failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Exiting.")
                sys.exit(1)


def process_log(log_data):
    """Process and write log to file"""
    try:
        # Parse JSON log
        log_obj = json.loads(log_data)
        
        # Format log entry
        timestamp = log_obj.get('timestamp', datetime.now(datetime.timezone.utc).isoformat())
        level = log_obj.get('level', 'INFO')
        message = log_obj.get('message', str(log_obj))
        
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Write to file
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        # Also print to stdout
        print(f"Processed: {log_entry.strip()}")
        
    except Exception as e:
        print(f"Error processing log: {e}")


def callback(ch, method, properties, body):
    """Callback function for RabbitMQ consumer"""
    try:
        process_log(body.decode('utf-8'))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in callback: {e}")
        # Reject and requeue the message
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def main():
    """Main consumer loop"""
    print("Starting Log Consumer")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    print(f"Queue: {RABBITMQ_QUEUE}")
    print(f"Log File: {LOG_FILE}")
    
    connection, channel = connect_to_rabbitmq()
    
    # Set prefetch count to 1 for fair dispatch
    channel.basic_qos(prefetch_count=1)
    
    # Start consuming
    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    
    print("Waiting for messages. To exit press CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Interrupted. Closing connection...")
        channel.stop_consuming()
        connection.close()


if __name__ == '__main__':
    main()
