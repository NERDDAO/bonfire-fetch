"""
Simple uAgent integration with bonfires.ai
Based on ASI:One documentation examples
"""

from datetime import datetime
from uuid import uuid4
from uagents import Protocol, Agent, Context, Model
from openai import OpenAI
from uagents.setup import fund_agent_if_low
from uagents import Field
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

BONFIRES_API_BASE = os.getenv("BONFIRES_ENDPOINT")
ASI_ONE_API_KEY = os.getenv("ASI_ONE_API_KEY")
BONFIRES_ID = os.getenv("BONFIRES_ID")
AGENT_SEED_PHRASE = os.getenv("AGENT_SEED_PHRASE")


client = OpenAI(
    base_url="https://api.as1.ai/v1",
    api_key=ASI_ONE_API_KEY
)

# Create the agent
agent = Agent(
    name="bonfire_agent",
    port=8000,
    seed=AGENT_SEED_PHRASE,
    endpoint=["http://127.0.0.1:8000/submit"],
    mailbox=True
)

protocol = Protocol(spec=chat_protocol_spec)

# the subject that this assistant is an expert in
subject_matter = "organize a birthday party"

# Copy the address shown below
print(f"Your agent's address is: {agent.address}")

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# @protocol.on_interval(period=30.0)
# async def health_check(ctx: Context):
#     """Periodic health check of the bonfires API"""
#     try:
#         response = requests.get(f"{BONFIRES_API_BASE}/healthz")
#         if response.status_code == 200:
#             ctx.logger.info("Bonfires API is healthy")
#         else:
#             ctx.logger.warning(f"Bonfires API health check failed: {response.status_code}")
#     except Exception as e:
#         ctx.logger.error(f"Error checking bonfires API health: {e}")

@protocol.on_message(model=ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and store them in bonfire"""
    ctx.logger.info(f"Received message: {msg.message}")
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    ) 

       # collect up all the text chunks
    text = ''
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text 
    try:
        # Search in vector store
        search_data = {
            "bonfire_id": BONFIRES_ID,
            "additional_query": text
        }
        
        response = requests.post(
            f"{BONFIRES_API_BASE}/vector_store/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            results = response.json()
            ctx.logger.info(f"Search completed, found {len(results) if isinstance(results, list) else 'results'}")
            
            search_response = results
        else:
            ctx.logger.error(f"Search failed: {response.status_code}")
            search_response="No results found"
    except Exception as e:
        ctx.logger.error(f"Error performing search: {e}")
       
        # query the model based on the user question
    chat_response = 'I am afraid something went wrong and I am unable to answer your question at the moment'
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"""
        You are a helpful assistant who only answers questions about {subject_matter}. 
        You should use the search results to answer the user's question.
                """},
                {"role": "assistant", "content": search_response},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )
 
        chat_response = str(r.choices[0].message.content)
          # send the response back to the user
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.utcnow(),
            msg_id=uuid4(),
            content=[
                # we send the contents back in the chat message
                TextContent(type="text", text=chat_response),
                # we also signal that the session is over, this also informs the user that we are not recording any of the
                # previous history of messages.
                EndSessionContent(type="end-session"),
            ]
        ))
 
    except Exception as e:
        ctx.logger.exception('Error querying model')

    try:
        # Store the message in bonfire using the new vector_store/add_chunk endpoint
        add_chunk_data = {
            "content": f"{text}\n\n{chat_response}",
            "bonfire_id": BONFIRES_ID,
            "label": "Chat Message"
        }
        
        response = requests.post(
            f"{BONFIRES_API_BASE}/vector_store/add_chunk",
            json=add_chunk_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200 and response.json().get("success"):
            ctx.logger.info(f"Message stored in vector store for bonfire {BONFIRES_ID}")
            await ctx.send(sender, f"Message processed and stored in vector store for bonfire {BONFIRES_ID}")
        else:
            error_msg = response.json().get("message") if response.headers.get("Content-Type", "").startswith("application/json") else response.text
            ctx.logger.error(f"Failed to store message: {response.status_code} {error_msg}")
            await ctx.send(sender, f"Error storing message: {response.status_code} {error_msg}")
            
    except Exception as e:
        ctx.logger.error(f"Error processing message: {e}")
        await ctx.send(sender, f"Error processing message: {str(e)}")

@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    # we are not interested in the acknowledgements for this example, but they can be useful to
    # implement read receipts, for example.
    pass


agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    print(f"Starting bonfire agent: {agent.name}")
    print(f"Agent address: {agent.address}")
    print(f"Agent wallet address: {agent.wallet.address()}")
    
    # Run the agent
    agent.run() 