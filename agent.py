"""
Simple uAgent integration with bonfires.ai
Based on ASI:One documentation examples
"""

import asyncio
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from uagents import Field
import requests
import json

# Define message models
class ChatMessage(Model):
    message: str = Field(description="The message to process")
    bonfire_id: str = Field(default="default", description="The bonfire ID to use")

class SearchRequest(Model):
    query: str = Field(description="The search query")
    bonfire_id: str = Field(default="default", description="The bonfire ID to search in")

class SearchResponse(Model):
    results: list = Field(description="Search results")
    query: str = Field(description="The original query")

# Create the agent
agent = Agent(
    name="bonfire_agent",
    port=8000,
    seed="bonfire_agent_seed_phrase_here",
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Bonfires API configuration
BONFIRES_API_BASE = "<BONFIRES_API_BASE>"

@agent.on_interval(period=30.0)
async def health_check(ctx: Context):
    """Periodic health check of the bonfires API"""
    try:
        response = requests.get(f"{BONFIRES_API_BASE}/healthz")
        if response.status_code == 200:
            ctx.logger.info("Bonfires API is healthy")
        else:
            ctx.logger.warning(f"Bonfires API health check failed: {response.status_code}")
    except Exception as e:
        ctx.logger.error(f"Error checking bonfires API health: {e}")

@agent.on_message(model=ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and store them in bonfire"""
    ctx.logger.info(f"Received message: {msg.message}")
    
    try:
        # Store the message in bonfire
        ingest_data = {
            "content": msg.message,
            "bonfire_id": msg.bonfire_id,
            "title": "Chat Message",
            "metadata": {
                "source": "uagent",
                "sender": sender,
                "timestamp": ctx.storage.get("timestamp", "unknown")
            }
        }
        
        response = requests.post(
            f"{BONFIRES_API_BASE}/ingest_content",
            json=ingest_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            ctx.logger.info(f"Message stored in bonfire {msg.bonfire_id}")
            
            # Trigger taxonomy generation if this is a new bonfire
            if msg.bonfire_id != "default":
                taxonomy_response = requests.post(
                    f"{BONFIRES_API_BASE}/trigger_taxonomy",
                    json={"bonfire_id": msg.bonfire_id}
                )
                if taxonomy_response.status_code == 200:
                    ctx.logger.info(f"Taxonomy generation triggered for {msg.bonfire_id}")
            
            # Send confirmation back
            await ctx.send(sender, f"Message processed and stored in bonfire {msg.bonfire_id}")
        else:
            ctx.logger.error(f"Failed to store message: {response.status_code}")
            await ctx.send(sender, f"Error storing message: {response.status_code}")
            
    except Exception as e:
        ctx.logger.error(f"Error processing message: {e}")
        await ctx.send(sender, f"Error processing message: {str(e)}")

@agent.on_message(model=SearchRequest)
async def handle_search_request(ctx: Context, sender: str, msg: SearchRequest):
    """Handle search requests against bonfire content"""
    ctx.logger.info(f"Search request: {msg.query}")
    
    try:
        # Search in vector store
        search_data = {
            "bonfire_id": msg.bonfire_id,
            "additional_query": msg.query
        }
        
        response = requests.post(
            f"{BONFIRES_API_BASE}/vector_store/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            results = response.json()
            ctx.logger.info(f"Search completed, found {len(results) if isinstance(results, list) else 'results'}")
            
            # Send results back
            search_response = SearchResponse(
                results=results,
                query=msg.query
            )
            await ctx.send(sender, search_response)
        else:
            ctx.logger.error(f"Search failed: {response.status_code}")
            await ctx.send(sender, f"Search failed: {response.status_code}")
            
    except Exception as e:
        ctx.logger.error(f"Error performing search: {e}")
        await ctx.send(sender, f"Error performing search: {str(e)}")

if __name__ == "__main__":
    print(f"Starting bonfire agent: {agent.name}")
    print(f"Agent address: {agent.address}")
    print(f"Agent wallet address: {agent.wallet.address()}")
    
    # Run the agent
    agent.run() 