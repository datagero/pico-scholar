# PICO Scholar Backend 🚀

## Introduction

This document provides a comprehensive guide to setting up and running the backend services for PICO Scholar. The backend includes FastAPI for API endpoints, MySQL for data storage, and TiDB for vector search functionality. It supports PICO extraction, contextual search, and document management.

**Note:** The backend uses an **OPENAI API key** for three key functionalities:
1. **Enhanced PICO extraction** (a dataflow dependency).
2. **Conversion of natural language to scientific notation for filters** (a direct API call from our front-end).
3. **Contextual Summarization and RAG** (features available for local runs).


## Table of Contents
1. [Project Structure](#project-structure) 🗂️
2. [Setup Instructions](#setup-instructions) ⚙️
3. [API Endpoints](#api-endpoints) 🌐
4. [Database Configuration](#database-configuration) 📊
5. [AI Integration](#ai-integration) 🧠
6. [Ingestion Pipelines](#ingestion-pipelines) 🔄

## Project Structure 🗂️

```
backend/
├── .dockerignore
├── Dockerfile
├── Dockerfile.stage1
├── README.md
├── database/
│   ├── schemas.sql
│   └── mock_data/
│       ├── 16625675.pdf
│       ├── abstracts.csv
│       ├── abstracts2.csv
│       ├── pubmed/
│           ├── PMC-ids-small.csv
│           ├── pmcid_dict.pkl
│           ├── pubmed24n0541.csv
│           └── recovered_pico_data.json
├── lamatidb/
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── database_interfaces/
│   │   │   ├── database_interface.py
│   │   │   ├── tidb_interface.py
│   │   ├── index_interface.py
│   │   ├── metadata_interface.py
│   │   ├── mysql_ingestors/
│   │   │   ├── abstract_ingestor.py
│   │   ├── query_interface.py
│   │   ├── run_streamlit.py
│   │   ├── settings_manager.py
│   │   ├── streamlit_app.py
│   │   ├── tidb_loaders/
│   │   │   ├── vector_loader_interface.py
│   ├── pipelines/
│   │   ├── orchestrator.py
│   │   ├── prepare_models.py
│   ├── requirements.txt
├── serverfastapi/
│   ├── .gitignore
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
```

- **`database/`**: Contains the MySQL schema and mock data for testing.
- **`lamatidb/`**: Includes interfaces and logic for interacting with MySQL, TiDB, and document processing.
- **`serverfastapi/`**: Contains the FastAPI application that serves the API for document ingestion, query processing, and PICO extraction.

## Setup Instructions ⚙️

### Docker - Option 1: Run Locally

1. **Set up MySQL Container with persistent local storage**:
   ```sh
   export MYSQL_ROOT_PASSWORD=my-secret-pw
   docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
   ```

2. [Optional test] **Connect to the MySQL server**:
   ```sh
   docker exec -it mysql-container mysql -uroot -p
   ```

3. **Run the backend server**:
   ```sh
   fastapi dev backend/serverfastapi/main.py
   ```

### Docker - Option 2: Run as a Containerized Application

1. **Build the Docker image**:
   From the `backend/` directory:
   ```sh
   docker build -t pico-backend .
   ```

2. **Create a Docker Network for services to communicate**:
   ```sh
   docker network create mynetwork
   ```

3. **Start the MySQL and backend containers**:
   ```sh
   export MYSQL_ROOT_PASSWORD=my-secret-pw
   docker run --network mynetwork --name mysql-container -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD -v $(pwd)/mysql_data:/var/lib/mysql -p 3306:3306 -d mysql:latest
   docker run --network mynetwork --env-file .env_docker --name pico-backend -p 8000:8000 -p 8501:8501 pico-backend
   ```

### Development Setup for Python Environment

If you're working in development and need to build the Python environment and (optionally) push it to the registry:
```sh
docker build --no-cache -t pico-env-builder --target pico-env-builder -f Dockerfile.stage1 .
docker tag pico-env-builder datagero/pico-env-builder:latest
docker push datagero/pico-env-builder:latest
```

If you need to build the pico-backend environment and push it to docker registry:
```sh
docker build --no-cache --platform linux/amd64 --target pico-backend -t datagero/pico-backend:latest -f Dockerfile .
docker push datagero/pico-backend:latest
```

## API Endpoints 🌐

| Endpoint | Method | Description |
| --- | --- | --- |
| `/projects/{project_id}/search/` | POST | Perform a search within the project's dataset. |
| `/projects/{project_id}/get_status/{status}` | GET | Retrieve documents by funnel stage and status. |
| `/projects/{project_id}/documents/{document_ids}/status/{status}` | PATCH | Update the status of specific documents. |
| `/projects/{project_id}/document/{document_id}/archive/{is_archived}` | PATCH | Archive or unarchive a document. |
| `/translate_terms/` | POST | Translate terms to scientific notation using ChatGPT. |
| `/projects/{project_id}/semantic_search/` | POST | Perform a semantic search within the dataset. |
| `/projects/{project_id}/chat/document/{document_id}` | POST | Start a Streamlit session to explore a document. |

## Database Configuration 📊

We use two main databases:
1. **MySQL** for document metadata and general data storage.
2. **TiDB** for managing vector embeddings and performing efficient vector search for scientific documents.

## AI Integration 🧠

The backend integrates AI tools for:
- **PICO Extraction**: Extracting Population, Intervention, Comparison, and Outcome segments from documents.
- **Contextual Summarization and RAG**: AI-powered tools for document summarization and retrieval augmentation.

Make sure to set the `OPENAI_API_KEY` environment variable to enable these features.

## Ingestion Pipelines 🔄

The **`backend/lamatidb/pipelines/orchestrator.py`** file provides an entry point for running the ingestion pipelines locally and building the necessary databases.

### Purpose:
This file serves as a demo to showcase how data flows through the modules we've built, creating the databases and vector indexes required for document search and PICO extraction.

### Key Steps:
1. **Database Setup**:
   - Set up MySQL and TiDB databases if they don’t exist.
   - Populate the databases with mock data or PubMed datasets located in the `datalake/` folder.

2. **Data Ingestion**:
   - Ingest abstracts, PICO data, and full document data into the databases.
   - Use loaders and ingestors from `lamatidb/interfaces/` to process and load data into TiDB for vector search.

3. **Vector Indexing**:
   - Use the `IndexInterface` to create vector embeddings and store them in the TiDB vector store.
   - Perform similarity searches using the indexed data.

4. **Example Query**:
   - Run similarity searches or metadata-filtered queries using the `QueryInterface`.
   - You can experiment with PICO metadata filters and generate PICO summaries from stored data.


Here is the section explaining our interfaces in table format:

---

## Interfaces Overview

| Interface           | Purpose                                                                                   | Key Functions                                                                                                                                   | Usage Example                                                                                             |
|---------------------|-------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **`DatabaseInterface`**  | Encapsulates interactions with MySQL and TiDB for data management.                           | `setup_database()`, `create_database_if_not_exists()`, `create_tables()`, `fetch_data_from_db()`                                                 | Used for setting up MySQL/TiDB databases, executing queries, and managing table schemas.                 |
| **`Ingestor`**           | Base class for managing ingestion of abstract, full documents, and PICO data into MySQL.   | `process_csv()`, `process_blob()`, `insert_data()`, `fetch_unprocessed_pico_data()`                                                             | Used for ingesting documents, abstracts, and extracting PICO metadata for storage in MySQL/TiDB.         |
| **`AbstractIngestor`**   | Subclass of `Ingestor` for managing abstract ingestion and PICO metadata processing.        | `process_csv()`, `process_pico_metadata()`, `recovery_load_pico_enhanced()`                                                                      | Handles ingestion of abstract data and PICO metadata extraction from CSV files.                           |
| **`FullDocumentIngestor`**| Subclass of `Ingestor` for ingesting full documents (e.g., PDFs) and their metadata.        | `process_blob()`, `download_full_document()`, `get_docID_mapper()`                                                                               | Manages full document ingestion and handling full-text documents for detailed processing.                 |
| **`LoaderPubMedAbstracts`**| Interface for loading and processing PubMed abstracts into LlamaIndex documents.            | `load_data()`, `process_data()`, `clean_data()`, `get_documents()`                                                                               | Loads PubMed abstracts from MySQL, processes them into document objects for vector search.                |
| **`LoaderPubMedFullText`** | Interface for loading full-text documents and converting them into LlamaIndex documents.     | `load_data()`, `process_data()`, `clean_data()`                                                                                                  | Loads and processes full-text PubMed documents (from PDFs or XMLs) for use in document search and retrieval.|
| **`IndexInterface`**     | Manages creation and retrieval of vector indexes for documents using TiDB as vector store. | `load_index_from_vector_store()`, `create_index()`, `get_index()`                                                                                | Loads or creates vector indexes for document embeddings, used for efficient document similarity search.    |
| **`QueryInterface`**     | Handles querying vector indexes and interacting with LLMs (e.g., OpenAI, Together).        | `configure_retriever()`, `assemble_query_engine()`, `perform_query()`, `query_chatgpt()`, `query_llm()`                                          | Executes semantic and metadata-filtered queries against vector indexes, integrates with LLMs for responses.|


### Application CRUD Operations Overview

The project uses **SQLAlchemy** for managing **MySQL** database models and **Pydantic** for validation. The `Query` model stores search queries, while the `Result` model contains metadata for each search result, including details like title, authors, abstract, and PICO elements. CRUD operations handle database interactions, with functions like `create_query` for adding new queries and `create_results` for inserting search results associated with a query. Pydantic schemas ensure data validation and serialization for queries and results. The CRUD logic is implemented in `crud.py`, with models defined in `models.py`.