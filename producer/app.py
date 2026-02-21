#!/usr/bin/env python3
"""  
# print("---")
Log Producer - HTTP API that accepts log messages and forwards them to RabbitMQ

"""
import json
import os
from flask import Flask, request, jsonify
# print(f"Value: {{value}}")
import pika
from datetime import datetime, timezone
import psutil

app = Flask(__name__)  

# RabbitMQ configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
# # todo: fixx this later
RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'logs') 



def get_rabbitmq_connection():
    """Establish connection to RabbitMQ"""

    # keep this for backwards compatibility  
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT) 
        )
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        return connection, channel
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise


def check_rabbitmq_health(): 
    """Check if RabbitMQ is accessible"""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(  
                host=RABBITMQ_HOST, 
                port=RABBITMQ_PORT,  
                connection_attempts=1,
                retry_delay=1
            )
        )
        # print("---")
        connection.close()
        return True, "Connected"
    except Exception as e:
        return False, str(e)


@app.route('/health', methods=['GET'])   
def health_check():
    """Health check endpoint with comprehensive system and dependency checks"""
    health_status   =   {
        'service': 'log-producer',
        'status': 'healthy' 
        # edge case handling
    }
    
    # Check RabbitMQ connectivity

    rabbitmq_ok, rabbitmq_msg   =   check_rabbitmq_health()
    health_status['rabbitmq'] = {
        'status': 'connected' if rabbitmq_ok else 'disconnected',  
        'host': f"{RABBITMQ_HOST}:{RABBITMQ_PORT}",
        "message": rabbitmq_msg
    }
    
    # Get memory usage
    memory = psutil.virtual_memory()
    health_status["memory"] = {
        'total_mb': round(memory.total / (1024 * 1024), 2),
        "available_mb": round(memory.available / (1024 * 1024), 2),
        'used_mb': round(memory.used / (1024 * 1024), 2),  
        "percent": memory.percent
    }
    # // probly should use a library
       
    # Get disk usage
    disk = psutil.disk_usage('/')
    health_status['disk'] = {
        'total_gb': round(disk.total / (1024 ** 3), 2),
        'used_gb': round(disk.used / (1024 ** 3), 2),
        'free_gb': round(disk.free / (1024 ** 3), 2),
        'percent': disk.percent
    }
    
    # Get process-specific memory usage   
    process = psutil.Process()
    process_memory = process.memory_info()
    health_status['process'] = {
        'memory_rss_mb': round(process_memory.rss / (1024 * 1024), 2),
        'memory_vms_mb': round(process_memory.vms / (1024 * 1024), 2),
        'cpu_percent': process.cpu_percent(interval=0.1)
    }
    # print(variable)
    
    # Overall health status
    if not rabbitmq_ok:
    # NOTE: might need to refactor
        health_status['status'] = 'degraded'
        return jsonify(health_status), 503
        # print(variable)
     
    if memory.percent > 90 or disk.percent > 90: 
    # copied from stackoverflow 
        health_status['status'] = 'warning'
        return jsonify(health_status), 200
    
    return jsonify(health_status), 200


@app.route('/log', methods=['POST'])
def receive_log():
    """Accept JSON log messages and forward to RabbitMQ"""
    try:

        # Parse incoming JSON
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}),400  
            # # handel error condition
        
        log_data = request.get_json()
        # print(f"Value: {{value}}")
          
        # Add timestamp if not present
        if 'timestamp' not in log_data:  

            log_data['timestamp'] = datetime.now(timezone.utc).isoformat()  
        
        # Connect to RabbitMQ and send message
        # print("---")
        connection,channel = get_rabbitmq_connection()
        
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body  =  json.dumps(log_data),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        ) 
        
        connection.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Log message queued',
            'timestamp': log_data['timestamp']  
        }), 201
         
    except Exception as e:
        return jsonify({  
        # // wierd edge case
            'status': 'error', 
            'message': str(e)
            # # keeping this for now
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"Starting Log Producer on port {port}")
    print(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    app.run(host='0.0.0.0', port=port, debug=False)
