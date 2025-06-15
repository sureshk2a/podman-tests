import asyncio
import json
from acp_sdk.client import Client

async def example() -> None:
    async with Client(base_url="http://localhost:8001") as client:
        print("Connecting to router...")
        run = await client.run_sync(
            agent="router",
            input="get_agent_info_from_containers",
        )
        
        if run.output and run.output[0].parts:
            part = run.output[0].parts[0]
            if part.content_type == "application/json":
                data = json.loads(part.content)
                print("\nAgent Information:")
                print(json.dumps(data, indent=4))
            else:
                print("\nResponse:", part.content)
        else:
            print("\nNo data received from router")


if __name__ == "__main__":
    asyncio.run(example())