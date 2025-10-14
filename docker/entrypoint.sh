#!/bin/bash
set -e

# Create required Airflow directories
mkdir -p /opt/airflow/logs
mkdir -p /opt/airflow/logs/scheduler
mkdir -p /opt/airflow/logs/dag_processor_manager
mkdir -p /opt/airflow/dags
mkdir -p /opt/airflow/plugins

# Set correct ownership and permissions for airflow user (UID 50000)
chown -R 50000:0 /opt/airflow/logs
chown -R 50000:0 /opt/airflow/dags
chown -R 50000:0 /opt/airflow/plugins

# Make directories readable/writable for airflow user
chmod -R 755 /opt/airflow/logs
chmod -R 755 /opt/airflow/dags
chmod -R 755 /opt/airflow/plugins

# Print status for debugging
echo "✓ Airflow directories initialized with correct permissions"
ls -la /opt/airflow/ | grep -E 'logs|dags|plugins'

# Run the actual command
exec "$@"