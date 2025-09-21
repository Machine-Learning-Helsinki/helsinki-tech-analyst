```mermaid
graph TD
    %% Define Styles
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Nginx fill:#9f9,stroke:#333,stroke-width:2px
    style Airflow fill:#ff9,stroke:#333,stroke-width:2px
    style Grafana fill:#ff9,stroke:#333,stroke-width:2px

    %% Subgraph for User Facing Services
    subgraph User Facing Services
        User["<br/>👤<br/>End User"]
        subgraph Browser
            Frontend["React Frontend<br/>(Q&A App)"]
            Dashboard["Streamlit Dashboard<br/>(Analytics)"]
        end
    end

    %% Subgraph for Core API & Data Store
    subgraph Core API & Data Store
        Nginx["Nginx<br/>(Reverse Proxy)"]
        FastAPI["FastAPI Backend<br/>(api_backend)"]
        Postgres["PostgreSQL DB<br/>(pgvector)"]
        OpenAI["OpenAI API<br/>(External LLM)"]
    end
    
    %% Subgraph for MLOps & Data Processing
    subgraph MLOps & Data Processing
        Airflow["Apache Airflow<br/>(Orchestrator)"]
        PipelineContainer["Data Pipeline Container<br/>(data_pipeline)"]
        Websites["External Websites<br/>(RSS Feeds)"]
    end

    %% Subgraph for Monitoring & Observability
    subgraph Monitoring & Observability
        Prometheus["Prometheus<br/>(Metrics Collector)"]
        Grafana["Grafana<br/>(Dashboards)"]
    end

    %% User Request Flow (Solid Arrows)
    User --> Browser
    Browser -- "HTTP Requests" --> Nginx
    Nginx -- "/api" --> FastAPI
    Nginx -- "/dashboard" --> Dashboard
    Nginx -- "/" --> Frontend
    FastAPI -- "Similarity Search<br/>(SQL Query with <=>) " --> Postgres
    FastAPI -- "Augmented Prompt" --> OpenAI
    OpenAI -- "Generated Answer" --> FastAPI
    Dashboard -- "SQL for Visuals" --> Postgres

    %% Data Ingestion Flow (Dashed Arrows)
    Airflow -.-> PipelineContainer
    PipelineContainer -. "Triggers Run" .-> Websites
    Websites -. "Fetches Data" .-> PipelineContainer
    PipelineContainer -. "Stores Articles & Embeddings" .-> Postgres

    %% Monitoring Flow (Dotted Arrows)
    FastAPI ~~~ "Exposes /metrics" ~~~> Prometheus
    Airflow ~~~ "Exposes Metrics" ~~~> Prometheus
    Prometheus ~~~ "Data Source" ~~~> Grafana
    User -- "Views Dashboards" --> Grafana
