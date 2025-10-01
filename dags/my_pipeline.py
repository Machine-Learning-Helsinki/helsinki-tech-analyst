"""
FINLAND RSS PIPELINE - MAIN DAG FILE
Modular Airflow DAG with separate fetch, transform, store, and main tasks
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import sys
import os


# Add current directory to Python path for module imports
sys.path.insert(0, os.path.dirname(__file__))

# Import functions from separate modules


# ==================== DAG CONFIGURATION ====================
default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    
}






# ==================== DAG DEFINITION ====================

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    dag_id="docker_pipeline_dag",
    default_args=default_args,
    description="Run ETL pipeline in a Docker container with Postgres dependency",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["etl", "docker", "postgres"],
) as dag:

    run_docker_pipeline = DockerOperator(
        task_id="run_docker_pipeline",
        image="ayushghimire95/data-pipeline:1.8",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        # Use the same Docker network as your docker-compose services
        network_mode="helsinki-tech-analyst_default",
        command="python -m src.data_pipeline.main" ,  # replace with your actual docker-compose network name
        mount_tmp_dir=False,
    )

    run_docker_pipeline
