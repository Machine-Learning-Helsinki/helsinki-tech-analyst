#!/bin/bash
# Create logs directory with proper permissions
mkdir -p /opt/airflow/logs
chmod 777 /opt/airflow/logs

# Run the actual command
exec "$@"