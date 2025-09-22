"""
FINLAND RSS PIPELINE - MAIN DAG FILE
Modular Airflow DAG with separate fetch, transform, store, and main tasks
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
import sys
import os
from data_pipeline.vector_db import vectordb

# Add current directory to Python path for module imports
sys.path.insert(0, os.path.dirname(__file__))

# Import functions from separate modules
try:
    from data_pipeline.fetch import install_packages, fetch_rss_data
    from data_pipeline.parse import transform_rss_data
    from data_pipeline.storage import store_rss_data
    from data_pipeline.main import pipeline_summary
    from data_pipeline.vector_db import vectordatabasePg
    print("✅ Successfully imported all pipeline modules")
except ImportError as e:
    print(f"❌ Failed to import pipeline modules: {e}")
    print("Make sure fetch.py, transform.py, storage.py, and main.py are in the same directory as this DAG")
    raise

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
        image="ayushghimire95/data-pipeline:1.5",
        api_version="auto",
        auto_remove=True,
        docker_url="unix://var/run/docker.sock",
        # Use the same Docker network as your docker-compose services
        network_mode="airflow_default",   # replace with your actual docker-compose network name
        command='/bin/bash -c "python /opt/airflow/dags/data_pipeline/main.py"',
        mount_tmp_dir=False,
    )

    run_docker_pipeline
