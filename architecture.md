# Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "uAgent Framework"
        UA[User Agent] --> |Chat Messages| BA[Bonfire Agent]
        BA --> |Responses| UA
        BA --> |Search Queries| UA
    end

    subgraph "Bonfires.ai Backend"
        BA --> |Ingest Content| IC[Ingest Content API]
        BA --> |Search| VS[Vector Store Search]
        BA --> |Taxonomy| TG[Taxonomy Generation]
        
        IC --> |Store| VDB[(Vector Database<br/>Weaviate)]
        VS --> |Query| VDB
        TG --> |Labels| VDB
        
        VDB --> |Chunks| CH[Content Chunks]
        VDB --> |Embeddings| EM[Vector Embeddings]
        VDB --> |Taxonomy| TX[Taxonomy Labels]
    end

    subgraph "Memory Flow"
        UA --> |Chat Output| BA
        BA --> |Store in Bonfire| IC
        IC --> |Persistent Memory| VDB
        VDB --> |Context Retrieval| VS
        VS --> |Relevant Context| BA
        BA --> |Enhanced Response| UA
    end

    subgraph "Query Flow"
        UA --> |Question| BA
        BA --> |Search Request| VS
        VS --> |Semantic Search| VDB
        VDB --> |Relevant Chunks| VS
        VS --> |Search Results| BA
        BA --> |Answer| UA
    end

    style BA fill:#e1f5fe
    style VDB fill:#f3e5f5
    style UA fill:#e8f5e8
    style IC fill:#fff3e0
    style VS fill:#fff3e0
    style TG fill:#fff3e0
```

## Data Flow Architecture

### 1. Memory Storage Flow
```
User Agent → Bonfire Agent → Ingest Content → Vector Database
     ↑                                           ↓
     ← Enhanced Response ← Context Retrieval ← Search
```

### 2. Query Processing Flow
```
User Question → Bonfire Agent → Vector Search → Relevant Context → Response
```

### 3. Taxonomy Generation Flow
```
Content Ingestion → Taxonomy Trigger → Label Generation → Vector Store Update
```

## Integration Components

### uAgent Framework
- **User Agent**: Client application or chat interface
- **Bonfire Agent**: Main integration agent handling communication
- **Protocol**: Standardized chat protocol for message exchange

### Bonfires.ai Backend
- **Ingest Content API**: Stores messages and documents
- **Vector Store Search**: Semantic search capabilities
- **Taxonomy Generation**: Automatic content categorization
- **Vector Database**: Persistent storage with embeddings

### Key Features
- **Persistent Memory**: All conversations stored in bonfires
- **Context Retrieval**: Semantic search for relevant information
- **Taxonomy Learning**: Automatic content organization
- **Real-time Processing**: Immediate response with context 
