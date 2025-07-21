"""
Simple client to test the bonfire uAgent
"""

import asyncio
from uagents import Agent, Model
from uagents import Field

# Define the same message models as in agent.py
class ChatMessage(Model):
    message: str = Field(description="The message to process")
    bonfire_id: str = Field(default="default", description="The bonfire ID to use")

class SearchRequest(Model):
    query: str = Field(description="The search query")
    bonfire_id: str = Field(default="default", description="The bonfire ID to search in")

class SearchResponse(Model):
    results: list = Field(description="Search results")
    query: str = Field(description="The original query")

# Create a client agent
client = Agent(
    name="test_client",
    port=8001,
    seed="test_client_seed_phrase_here",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# The bonfire agent address (you'll need to get this from the running agent)
BONFIRE_AGENT_ADDRESS = "agent1qfrdhuhl874z8zzvx3z34sftgl4ard9n5f4l9dfkce2dut3zds94zaupadm"

@client.on_message(model=str)
async def handle_response(ctx, sender: str, msg: str):
    """Handle responses from the bonfire agent"""
    print(f"Response from {sender}: {msg}")

@client.on_message(model=SearchResponse)
async def handle_search_response(ctx, sender: str, msg: SearchResponse):
    """Handle search responses from the bonfire agent"""
    print(f"Search results for '{msg.query}':")
    print(f"Found {len(msg.results)} results")
    for i, result in enumerate(msg.results[:3]):  # Show first 3 results
        print(f"  {i+1}. {result}")

async def test_chat_message():
    """Test sending a chat message to the bonfire agent"""
    print("Testing chat message...")
    
    message = ChatMessage(
        message="Hello! This is a test message from the uAgent client.",
        bonfire_id="test_bonfire"
    )
    
    await client.send(BONFIRE_AGENT_ADDRESS, message)
    print("Chat message sent!")

async def test_search():
    """Test searching in the bonfire"""
    print("Testing search...")
    
    search_req = SearchRequest(
        query="test message",
        bonfire_id="test_bonfire"
    )
    
    await client.send(BONFIRE_AGENT_ADDRESS, search_req)
    print("Search request sent!")

async def main():
    """Main test function"""
    print(f"Starting test client: {client.name}")
    print(f"Client address: {client.address}")
    
    # Wait a bit for the bonfire agent to start
    print("Waiting for bonfire agent to be ready...")
    await asyncio.sleep(5)
    
    # Test chat message
    await test_chat_message()
    
    # Wait a bit for processing
    await asyncio.sleep(3)
    
    # Test search
    await test_search()
    
    # Keep the client running to receive responses
    print("Client running... Press Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Client stopped")

if __name__ == "__main__":
    asyncio.run(main()) 