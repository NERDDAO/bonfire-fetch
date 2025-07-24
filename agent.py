"""
Simple uAgent integration with bonfires.ai
Based on ASI:One documentation examples
"""

from datetime import datetime, timezone
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
    base_url="https://api.asi1.ai/v1",
    api_key=ASI_ONE_API_KEY
)

# Create the agent
agent = Agent(
    name="bonfire_agent",
    port=8001,
    seed=AGENT_SEED_PHRASE,
    mailbox=True
)

protocol = Protocol(spec=chat_protocol_spec)

# the subject that this assistant is an expert in
subject_matter = "organize a birthday party"

# Copy the address shown below
print(f"Your agent's address is: {agent.address}")

# Fund the agent if needed
fund_agent_if_low(agent.wallet.address())

# Helper function to send error messages
async def send_error(ctx, sender, error_text):
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=error_text),
            EndSessionContent(type="end-session"),
        ]
    ))

@protocol.on_message(model=ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    ctx.logger.info(f"Received message: {msg.content}")
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id))

    text = ''.join(item.text for item in msg.content if isinstance(item, TextContent))

    # 1. Search in vector store
    try:
        search_data = {"bonfire_id": BONFIRES_ID, "additional_query": text}
        response = requests.post(f"{BONFIRES_API_BASE}/vector_store/search", json=search_data, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            search_response = response.json()
            ctx.logger.info(f"Search completed, found {len(search_response) if isinstance(search_response, list) else 'results'}")
        else:
            ctx.logger.error(f"Search failed: {response.status_code}")
            await send_error(ctx, sender, f"Search failed: {response.status_code}")
            return
    except Exception as e:
        ctx.logger.error(f"Error performing search: {e}")
        await send_error(ctx, sender, f"Error performing search: {str(e)}")
        return

    # 2. Query the model
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant who is an expert in {subject_matter}. Use the search results to answer the user's question."},
                {"role": "assistant", "content": search_response},
                {"role": "user", "content": text},
            ],
            max_tokens=2048,
        )
        chat_response = str(r.choices[0].message.content)
        await ctx.send(sender, ChatMessage(
            timestamp=datetime.now(timezone.utc),
            msg_id=uuid4(),
            content=[
                TextContent(type="text", text=chat_response),
                EndSessionContent(type="end-session"),
            ]
        ))
    except Exception as e:
        ctx.logger.error(f"Error querying model: {e}")
        await send_error(ctx, sender, f"Error querying model: {str(e)}")
        return

    # 3. Store the message in bonfire
    try:
        add_chunk_data = {
            "content": f"{text}\n\n{chat_response}",
            "bonfire_id": BONFIRES_ID,
            "label": "Chat Message"
        }
        response = requests.post(f"{BONFIRES_API_BASE}/vector_store/add_chunk", json=add_chunk_data, headers={"Content-Type": "application/json"})
        if response.status_code == 200 and response.json().get("success"):
            ctx.logger.info(f"Message stored in vector store for bonfire {BONFIRES_ID}")
            await ctx.send(sender, ChatMessage(
                timestamp=datetime.now(timezone.utc),
                msg_id=uuid4(),
                content=[
                    TextContent(type="text", text=f"Message processed and stored in vector store for bonfire {BONFIRES_ID}"),
                    EndSessionContent(type="end-session"),
                ]
            ))
        else:
            error_msg = response.json().get("message") if response.headers.get("Content-Type", "").startswith("application/json") else response.text
            ctx.logger.error(f"Failed to store message: {response.status_code} {error_msg}")
            await send_error(ctx, sender, f"Error storing message: {response.status_code} {error_msg}")
            return
    except Exception as e:
        ctx.logger.error(f"Error processing message: {e}")
        await send_error(ctx, sender, f"Error processing message: {str(e)}")
        return

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