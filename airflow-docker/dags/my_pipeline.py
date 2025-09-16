"""
FINLAND RSS PIPELINE - MAIN DAG FILE
Modular Airflow DAG with separate fetch, transform, store, and main tasks
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys
import os

# Add current directory to Python path for module imports
sys.path.insert(0, os.path.dirname(__file__))

# Import functions from separate modules
try:
    from data_pipeline.fetch import install_packages, fetch_rss_data
    from data_pipeline.parse import transform_rss_data
    from data_pipeline.storage import store_rss_data
    from data_pipeline.main import pipeline_summary
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
with DAG(
    dag_id="finland_rss_modular_etl_pipeline",
    default_args=default_args,
    description='Modular Finland RSS ETL pipeline with separate fetch, transform, store, and summary tasks',
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",  # Run daily at midnight
    catchup=False,
    max_active_runs=1,  # Prevent overlapping runs
    tags=['rss', 'finland', 'etl', 'modular', 'news'],
) as dag:

    # ==================== TASK DEFINITIONS ====================
    
    # Task 0: Install Required Packages
    

    # Task 1: Fetch RSS Data
    fetch_data_task = PythonOperator(
        task_id="fetch_rss_data",
        python_callable=fetch_rss_data,
        doc_md="""
        ## Fetch RSS Data
        
        **Purpose**: Downloads and collects RSS feeds from Finnish news sources
        
        **RSS Sources processed**:
        - Hämeen Sanomat RSS Feed
        - Helsinki Times RSS Feed  
        - Yle RSS Feed
        - Finland Today RSS Feed
        - Länsi-Savo RSS Feed
        
        **Process**:
        1. Attempts to fetch each RSS feed
        2. Validates feed structure and content
        3. Converts to serializable format for XCom
        4. Handles network errors and invalid feeds
        
        **Output**: Dictionary with raw RSS entries per source
        **XCom Key**: Stored automatically for next task
        """,
        pool='default_pool',
    )

    # Task 2: Transform RSS Data
    transform_data_task = PythonOperator(
        task_id="transform_rss_data", 
        python_callable=transform_rss_data,
        doc_md="""
        ## Transform RSS Data
        
        **Purpose**: Clean, translate, and structure RSS feed data
        
        **Transformation steps**:
        1. **Language Detection**: Identify Finnish content
        2. **Translation**: Finnish → English using Google Translate
        3. **HTML Cleaning**: Remove HTML tags from summaries
        4. **Data Structuring**: Format for database storage
        5. **Validation**: Ensure data quality and completeness
        
        **Input**: Raw RSS entries from fetch task (via XCom)
        **Output**: Clean, translated article data ready for storage
        **Features**:
        - Automatic language detection
        - Robust error handling for translation failures
        - HTML sanitization with BeautifulSoup
        - Data validation and enrichment
        """,
        pool='default_pool',
    )

    # Task 3: Store Data in Database
    store_data_task = PythonOperator(
        task_id="store_rss_data",
        python_callable=store_rss_data,
        doc_md="""
        ## Store RSS Data
        
        **Purpose**: Persist articles to PostgreSQL database
        
        **Database operations**:
        1. **Connection**: Connect to PostgreSQL using environment variables
        2. **Table Management**: Create articles table and indexes if needed
        3. **Duplicate Detection**: Skip articles that already exist (by URL)
        4. **Batch Insert**: Efficiently store new articles
        5. **Statistics**: Track storage success/failure rates
        
        **Database Schema**:
        ```sql
        CREATE TABLE articles (
            id SERIAL PRIMARY KEY,
            link_name TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published TEXT,
            summary TEXT,
            authors TEXT[],
            tags TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ```
        
        **Input**: Transformed articles from transform task (via XCom)
        **Output**: Storage statistics and database health metrics
        **Features**:
        - Automatic table and index creation
        - Duplicate prevention by URL
        - Comprehensive error handling
        - Performance optimization with indexes
        """,
        pool='default_pool',
    )

    # Task 4: Pipeline Summary and Additional Processing
    pipeline_summary_task = PythonOperator(
        task_id="pipeline_summary",
        python_callable=pipeline_summary,
        doc_md="""
        ## Pipeline Summary & Final Processing
        
        **Purpose**: Aggregate results and perform final pipeline tasks
        
        **Summary generation**:
        1. **Results Aggregation**: Collect results from all previous tasks
        2. **Metrics Calculation**: Compute efficiency, quality, and health scores
        3. **Comprehensive Reporting**: Generate detailed pipeline summary
        4. **Additional Processing**: Trigger downstream tasks if needed
        
        **Metrics calculated**:
        - **Efficiency Rate**: (Stored articles / Fetched articles) × 100
        - **Data Quality Score**: 0-100 based on fetch/transform/store success rates
        - **Sources Health**: Percentage of working RSS sources
        
        **Additional processing (configurable)**:
        - Trigger ML embeddings processing for new articles
        - Send pipeline completion notifications
        - Update monitoring dashboards
        - Perform cleanup tasks
        
        **Input**: Results from all previous tasks (via XCom)
        **Output**: Complete pipeline summary with all statistics
        """,
        pool='default_pool',
    )

    # ==================== TASK DEPENDENCIES ====================
    # Define the ETL pipeline flow
    fetch_data_task >> transform_data_task >> store_data_task >> pipeline_summary_task

    # ==================== DAG DOCUMENTATION ====================
    dag.doc_md = """
    # Finland RSS ETL Pipeline
    
    ## Overview
    This DAG implements a complete ETL (Extract, Transform, Load) pipeline for processing RSS feeds from Finnish news sources. The pipeline is designed to run daily and consists of five sequential tasks.
    
    ## Pipeline Architecture
    
    ```
    📦 Install Packages
           ↓
    📡 Fetch RSS Data  
           ↓
    🔧 Transform Data
           ↓  
    💾 Store in Database
           ↓
    📊 Pipeline Summary
    ```
    
    ## Key Features
    
    ### 🔄 **Modular Design**
    - Each task is in a separate module for maintainability
    - Clean separation of concerns (fetch, transform, store, summary)
    - Easy to test and debug individual components
    
    ### 🛡️ **Robust Error Handling**  
    - Network timeouts and HTTP errors handled gracefully
    - Database connection failures with automatic retry
    - Translation service failures with fallback to original text
    - Comprehensive logging for debugging
    
    ### 📊 **Data Quality & Monitoring**
    - Duplicate detection prevents data redundancy
    - Data validation ensures article completeness  
    - Performance metrics and health scoring
    - Comprehensive pipeline statistics
    
    ### 🌐 **Multi-language Support**
    - Automatic Finnish to English translation
    - Language detection to avoid unnecessary translation
    - HTML cleaning and text normalization
    
    ## Configuration
    
    ### Environment Variables
    Set these in your Airflow environment:
    ```bash
    DB_HOST=your_postgresql_host
    DB_PORT=5432  
    DB_USER=your_username
    DB_PASSWORD=your_password
    DB_NAME=your_database_name
    ```
    
    ### RSS Sources
    Currently processes these Finnish news sources:
    - Hämeen Sanomat
    - Helsinki Times
    - Yle (Finnish Broadcasting Company)
    - Finland Today
    - Länsi-Savo
    
    ## Database Schema
    Articles are stored in PostgreSQL with this structure:
    - **id**: Auto-incrementing primary key
    - **link_name**: RSS source name  
    - **title**: Article title (translated to English)
    - **link**: Unique article URL
    - **published**: Publication date/time
    - **summary**: Article summary (translated and cleaned)
    - **authors**: Array of author names
    - **tags**: Array of article tags
    - **created_at**: Record creation timestamp
    - **updated_at**: Record update timestamp
    
    ## Monitoring & Alerts
    The pipeline provides comprehensive monitoring:
    - Task-level success/failure tracking
    - Data quality metrics and scoring
    - RSS source health monitoring  
    - Performance and efficiency metrics
    
    ## Extending the Pipeline
    To add new RSS sources, edit the `finland_rss_feeds` list in `fetch.py`.
    To add new processing steps, create additional tasks and wire them into the dependency chain.
    """