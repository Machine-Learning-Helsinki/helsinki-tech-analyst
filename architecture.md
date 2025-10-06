# Ask Salmiakki: System Architecture

## 1. Guiding Principles

The architecture of **Ask Salmiakki** is designed around a set of modern software engineering and MLOps principles. The primary goal is to create a system that is modular, scalable, observable, and automated.

*   **Service-Oriented Design**: Each core component (API, dashboard, data pipeline) is treated as a distinct service with a single responsibility. This promotes separation of concerns and independent development.
*   **Containerization First**: All services are designed to be run within **Docker** containers, ensuring a consistent and reproducible environment from local development to production.
*   **Infrastructure as Code**: The entire multi-service environment is defined declaratively using **Docker Compose**, allowing the whole stack to be brought up or down with simple commands.
*   **Automation & Orchestration**: Manual tasks are minimized. The data ingestion pipeline is fully automated and scheduled by **Apache Airflow**.
*   **Observability**: The system is not a "black box." It is designed to be monitored, with key performance indicators exposed via **Prometheus** and visualized in **Grafana**.

---

## 2. Architectural Diagram

This diagram provides a high-level visual representation of the components and their interactions. The architecture is divided into logical layers: User Facing Services, Core API & Data Store, MLOps & Data Processing, and Monitoring.

```mermaid
graph TD
    %% Define Node Styles
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Nginx fill:#9f9,stroke:#333,stroke-width:2px
    style Airflow fill:#ff9,stroke:#333,stroke-width:2px
    style Grafana fill:#ff9,stroke:#333,stroke-width:2px
    style GoogleAI fill:#87CEFA,stroke:#333,stroke-width:2px

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
        GoogleAI["Google AI Platform<br/>(Gemini Pro)"]
    end
    
    %% Subgraph for MLoPS & Data Processing
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

    %% User Request Flow
    User --> Browser
    Browser -- "HTTP Requests" --> Nginx
    Nginx --> FastAPI & Frontend & Dashboard
    FastAPI -- "Similarity Search (SQL)" --> Postgres
    FastAPI -- "Augmented Prompt" --> GoogleAI
    GoogleAI --> FastAPI
    Dashboard -- "SQL for Visuals" --> Postgres

    %% Data Ingestion Flow
    Airflow -. "Triggers Run" .-> PipelineContainer
    PipelineContainer -. "Fetches Data" .-> Websites
    PipelineContainer -. "Stores Articles & Embeddings" .-> Postgres

    %% Monitoring Flow
    FastAPI -->|Exposes /metrics| Prometheus
    Airflow -->|Exposes Metrics| Prometheus
    Prometheus -->|Data Source| Grafana
    User -->|Views Dashboards| Grafana
    
    %% Link Styles
    linkStyle 12 stroke:#888,stroke-width:2px,stroke-dasharray: 3 3
    linkStyle 13 stroke:#888,stroke-width:2px,stroke-dasharray: 3 3
    linkStyle 14 stroke:#888,stroke-width:2px,stroke-dasharray: 3 3
    linkStyle 15 stroke:#888,stroke-width:2px,stroke-dasharray: 3 3
