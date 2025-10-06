# Ask Salmiakki: Technical Design Document

This document provides a detailed breakdown of the core components, data flows, and architectural decisions for the Ask Salmiakki project. It is intended for a technical audience interested in the implementation details and design rationale.

---

## 1. Component Deep Dive

### 1.1. Frontend & User Interface Layer
*   **React Q&A App**: A Single Page Application (SPA) providing the primary conversational interface. Its sole responsibility is to manage UI state and communicate with the backend API.
*   **Streamlit Dashboard**: A Python-native data application that connects directly to the PostgreSQL database for read-only analytical queries. This choice allows for rapid development of data visualizations without needing to write a separate JavaScript frontend.
*   **Nginx Reverse Proxy**: Acts as the single entry point for all incoming web traffic. It routes requests to the appropriate service (React, FastAPI, or Streamlit) based on the URL path. This provides a unified access point and can handle SSL termination and load balancing in a production environment.

### 1.2. Backend & ML Core
*   **FastAPI Backend**: The high-performance API server. FastAPI was chosen for its asynchronous capabilities (ideal for I/O-bound tasks like API calls and database queries), automatic data validation via Pydantic, and self-generating OpenAPI documentation.
*   **RAG & Embedding Logic**: This is the application's "brain." A key architectural decision was to implement a **custom hashing vectorizer** for embeddings. This avoids the heavy dependency of a large transformer model, making the embedding process lightweight and extremely fast, which is ideal for a containerized pipeline. For generation, we interface with the powerful **Google Gemini Pro** model.

### 1.3. Data & Persistence Layer
*   **PostgreSQL with `pgvector`**: We made a strategic decision to consolidate our data storage. Instead of managing a separate relational database and a dedicated vector database, we use PostgreSQL for both. The `pgvector` extension allows for highly efficient similarity searches directly within the same database that stores our article metadata. This simplifies the infrastructure, reduces operational overhead, and guarantees data consistency.

### 1.4. MLOps & Automation Layer
*   **Apache Airflow**: The industry-standard workflow orchestrator. Airflow is responsible for scheduling and executing our data pipeline on a daily basis. Its role is to ensure the pipeline runs reliably, with built-in support for retries, logging, and monitoring of job status. We use the **`DockerOperator`** to run our pipeline script within its own isolated, containerized environment.
*   **Docker & Docker Compose**: Docker provides containerization for each service, ensuring dependency isolation and reproducibility. Docker Compose orchestrates the multi-container environment for local development, defining the services, networks, and volumes needed to run the entire stack.

### 1.5. Monitoring & Observability Layer
*   **Prometheus & Grafana**: This is the standard open-source stack for metrics-based monitoring. The FastAPI application is instrumented to expose performance metrics (latency, request counts, error rates) on a `/metrics` endpoint. Prometheus scrapes this data periodically, storing it in a time-series database. Grafana then queries Prometheus to build real-time dashboards, providing critical insights into the health and performance of the system.

---

## 2. Data and Request Flows

### 2.1. User Query Flow (Synchronous)
This flow describes the real-time interaction when a user asks a question.

1.  A user submits a question through the React frontend.
2.  Nginx routes the `/api/ask` request to the FastAPI backend.
3.  FastAPI generates an embedding for the question using the custom hashing vectorizer.
4.  It queries the PostgreSQL database with a `pgvector` similarity search to find the most relevant articles (the context).
5.  FastAPI constructs a detailed prompt containing the question and context, and sends it to the Google Gemini API.
6.  The generated answer is returned to the frontend and displayed to the user.

### 2.2. Data Ingestion Flow (Asynchronous, Batch)
This flow describes the automated, offline process for keeping the database up-to-date.

1.  The Airflow Scheduler triggers the data pipeline DAG based on its schedule (e.g., daily).
2.  Airflow executes a task using the `DockerOperator`, which starts a new container from our data pipeline image.
3.  The Python script inside the container fetches data from external RSS feeds.
4.  It filters, processes, and generates embeddings for each new article.
5.  Finally, it connects to the PostgreSQL database and stores both the article metadata and its corresponding vector embedding.

---

## 3. Future Considerations & Scalability

This project is built with scalability in mind. While the current Docker Compose setup is ideal for development, the following steps outline a clear path to a production-grade, scalable deployment.

*   **Deployment to Kubernetes**: The service-oriented, containerized architecture is designed for a seamless transition to a container orchestration platform like **Kubernetes (EKS, GKE, AKS)**. This would provide auto-scaling, self-healing, and rolling updates for the API and other services.
*   **Managed Cloud Services**: To reduce operational burden and improve reliability, the self-hosted components would be migrated to managed cloud services in a production environment:
    *   **PostgreSQL**: -> **Amazon RDS** or **Google Cloud SQL**.
    *   **Apache Airflow**: -> **Managed Workflows for Apache Airflow (MWAA)** or **Google Cloud Composer**.
*   **CI/CD Automation**: A CI/CD pipeline (e.g., using **GitHub Actions**) would be implemented to automate the following processes on every code push:
    1.  Running unit and integration tests.
    2.  Building and pushing new Docker images to a container registry (e.g., ECR, GCR).
    3.  Deploying the updated images to the Kubernetes cluster.
*   **Dedicated Vector Search**: While `pgvector` is highly efficient for this project's scale, a system with hundreds of millions of documents might benefit from migrating the vector search component to a dedicated, highly scalable service like **Pinecone** or **Weaviate**.
