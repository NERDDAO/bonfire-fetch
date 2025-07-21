# Bonfires.ai API Investigation Notes

## API Overview
- **Base URL**: `<API-BASE-URL>`
- **API Name**: kEngram Analysis API
- **Version**: 2.0
- **Description**: Lean API for purpose-driven document analysis using kEngrams
- **Documentation**: Available at `/docs` (Swagger UI)
- **OpenAPI Spec**: Available at `/openapi.json`

## Health Check
- **Endpoint**: `GET /healthz`
- **Status**: ✅ Working
- **Response**: 
  ```json
  {
    "status": "ok",
    "api": "kEngram Analysis",
    "version": "2.0",
    "job_system": {
      "status": "ok",
      "active_jobs": 0
    }
  }
  ```

## Core API Endpoints

### 1. Content Ingestion
- **Endpoint**: `POST /ingest_content`
- **Purpose**: Ingest content into the system for processing
- **Request Schema**: `IngestContentRequest`
  - `content` (string, required): The content to ingest
  - `bonfire_id` (string, optional): Defaults to "default"
  - `title` (string, optional): Title for the content
  - `metadata` (object, optional): Additional metadata

### 2. Taxonomy Management
- **Endpoint**: `POST /trigger_taxonomy`
- **Purpose**: Manually trigger taxonomy generation for a specific bonfire
- **Request Schema**: `TaxonomyTriggerRequest`
  - `bonfire_id` (string, required): The bonfire to generate taxonomy for

### 3. Content Labeling
- **Endpoint**: `POST /label_chunks`
- **Purpose**: Label chunks with taxonomy categories for a specific bonfire
- **Request Schema**: `LabelChunksRequest`
  - `bonfire_id` (string, required): The bonfire ID
  - `is_multi_label` (boolean, optional): Defaults to false

- **Endpoint**: `POST /labeling/hybrid`
- **Purpose**: Run hybrid labeling (vector + LLM) for a bonfire
- **Request Schema**: `HybridLabelingRequest`
  - `bonfire_id` (string, required): The bonfire ID
  - `is_multi_label` (boolean, optional): Defaults to false
  - `taxonomy_run_id` (string, optional): Specific taxonomy run ID
  - `vector_threshold` (number, optional): Defaults to 0.7

### 4. Vector Store Operations
- **Setup**: `POST /vector_store/setup`
  - Purpose: Setup Weaviate collections and populate with MongoDB data
  - Query param: `run_id` (optional)

- **Search**: `POST /vector_store/search`
  - Purpose: Search for chunks in Weaviate based on bonfire_id, labels, and optional query
  - Request Schema: `VectorSearchRequest`
    - `bonfire_id` (string, required): The bonfire ID
    - `labels` (array of strings, optional): Labels to filter by
    - `additional_query` (string, optional): Additional search query

- **Search by Labels**: `POST /vector_store/search_labels`
  - Purpose: Search for top matching labels based on chunk text
  - Request Schema: `SearchLabelsRequest`
    - `chunk_text` (string, required): Text to search labels for
    - `certainty_threshold` (number, optional): Defaults to 0.6

- **Search by Taxonomy ID**: `POST /vector_store/search_by_taxonomy_id`
  - Purpose: Search for chunks based on taxonomy IDs
  - Request Schema: `VectorSearchByTaxonomyRequest`
    - `bonfire_id` (string, required): The bonfire ID
    - `taxonomy_ids` (array of strings, optional): Taxonomy IDs to filter by
    - `additional_query` (string, optional): Additional search query

- **Update Labels**: `POST /vector_store/update_labels`
  - Purpose: Update vector store labels for a specific bonfire and run
  - Query params: `bonfire_id` (required), `run_id` (required)

- **Get Chunks**: `GET /vector_store/chunks/{bonfire_id}`
  - Purpose: Get labeled chunks from Weaviate for a specific bonfire
  - Query param: `limit` (optional, defaults to 10)

- **Clear Chunks**: `POST /vector_store/clear_chunks`
  - Purpose: Clear all chunks for a specific bonfire from Weaviate
  - Request Schema: `ClearChunksRequest`
    - `bonfire_id` (string, required): The bonfire ID

### 5. Summary Generation
- **Endpoint**: `POST /generate_summaries`
- **Purpose**: Generate summaries for a specific bonfire and run, tracked as a job
- **Request Schema**: `GenerateSummariesRequest`
  - `bonfire_id` (string, required): The bonfire ID

### 6. Data Retrieval
- **Get Labeled Chunks**: `GET /bonfire/{bonfire_id}/labeled_chunks`
  - Purpose: Get all labeled chunks for a bonfire organized by taxonomy labels

### 7. Job Management
- **Get Job Status**: `GET /jobs/{job_id}/status`
  - Purpose: Get status of a specific job

- **Get Recent Jobs**: `GET /jobs`
  - Purpose: Get recent jobs with optional filtering
  - Query params:
    - `bonfire_id` (optional): Filter by bonfire ID
    - `workflow_type` (optional): Filter by workflow type
    - `limit` (optional): Defaults to 50

- **Get Active Jobs**: `GET /jobs/active`
  - Purpose: Get all currently running jobs

## Key Concepts

### Bonfire
- A bonfire appears to be a container/workspace for document analysis
- Each bonfire has a unique ID
- Multiple operations can be performed on a single bonfire

### Taxonomy
- The system generates taxonomies for documents
- Taxonomies are used to categorize and label content chunks
- Can be triggered manually or generated automatically

### Vector Store (Weaviate)
- Uses Weaviate as the vector database
- Stores document chunks with embeddings
- Supports semantic search and filtering by labels/taxonomy

### Jobs
- Long-running operations are tracked as jobs
- Jobs can be monitored for status and progress
- Examples: summary generation, taxonomy generation

## Integration Notes for uAgent Framework

### Data Flow Architecture
1. **Ingest**: Content is ingested into a bonfire via `/ingest_content`
2. **Process**: Taxonomy is generated and chunks are labeled
3. **Store**: Content is stored in vector database (Weaviate)
4. **Query**: Semantic search can be performed on stored content
5. **Retrieve**: Relevant chunks can be retrieved for agent responses

### Key Integration Points
- **Memory Storage**: Use bonfire as persistent memory store for agent conversations
- **Context Retrieval**: Use vector search to find relevant context for agent responses
- **Taxonomy Learning**: Leverage taxonomy generation for better content organization
- **Job Monitoring**: Track long-running operations through job system

### Technical Considerations
- All endpoints return JSON responses
- Error responses follow standard HTTP status codes
- Job-based operations for long-running tasks
- Vector search supports both semantic and label-based filtering 
