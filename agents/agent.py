import asyncio
from collections.abc import AsyncGenerator

from acp_sdk.models import Message
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()


@server.agent(name="sample_agent", description="A sample agent")
async def agent(input: list[Message], context: Context) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Agent"""
    print(f"Agent received message: {input}")
    for message in input:
        await asyncio.sleep(0.5)
        yield {"thought": "I should do something"}
        await asyncio.sleep(0.5)
        yield {"message": message}


server.run(host="0.0.0.0", port=8000) 