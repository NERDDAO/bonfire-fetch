# Fetch Bonfire - uAgent Integration

This is an agent integration between bonfires.ai and ASI:One uAgent framework.

Bonfires provides a contextual framework to process unstructured data while the uAgents bring infrastructure for distribution of knowledge and agentic frameworks.

Bonfires is a semantic back end that creates taxonomies for documents and stores them in vector storage. The service can ingest documents and use chunk search to find contextual data for the agent.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Bonfire Agent

```bash
python agent.py
```

The agent will start and display its address. Note this address for the client configuration.

### 3. Update Client Configuration

Edit `client.py` and update the `BONFIRE_AGENT_ADDRESS` variable with the address from step 2.

### 4. Run the Test Client

In a new terminal:

```bash
python client.py
```

## Architecture

### Data Flow
1. **Ingest**: Content is ingested into a bonfire via `/ingest_content`
2. **Process**: Taxonomy is generated and chunks are labeled
3. **Store**: Content is stored in vector database (Weaviate)
4. **Query**: Semantic search can be performed on stored content
5. **Retrieve**: Relevant chunks can be retrieved for agent responses

### Integration Points
- **Memory Storage**: Use bonfire as persistent memory store for agent conversations
- **Context Retrieval**: Use vector search to find relevant context for agent responses
- **Taxonomy Learning**: Leverage taxonomy generation for better content organization
- **Job Monitoring**: Track long-running operations through job system

## API Documentation

See `bonfires_api_notes.md` for detailed API documentation and investigation notes.

## TODO

1. ✅ Map bonfires API calls and data structure
2. Create an architecture diagram for the integration:
   - ✅ Create data store on bonfires
   - ✅ Create query flow: infer, search, reply
   - ✅ Create memory flow: chat outputs into bonfire, (mailbox processing)
   - Deploy uAgent

## Files

- `agent.py` - Main uAgent that integrates with bonfires.ai
- `client.py` - Test client for the uAgent
- `requirements.txt` - Python dependencies
- `bonfires_api_notes.md` - API investigation notes
- `README.md` - This file 