import requests
import json
from datetime import datetime, timezone
from acp_sdk.models import Message, MessagePart

def test_router():
    url = "http://localhost:8001/runs"
    headers = {"Content-Type": "application/json"}
    
    # Create a proper Message object
    message = Message(parts=[
        MessagePart(
            content="Howdy!",
            content_type="text/plain",
            content_encoding="plain"
        )
    ])
    
    # Convert Message to dict and handle datetime serialization
    message_dict = message.model_dump()
    now = datetime.now(timezone.utc).isoformat()
    message_dict["created_at"] = now
    message_dict["completed_at"] = now
    
    data = {
        "agent_name": "router",
        "input": [message_dict]
    }
    
    print("Sending request to router...")
    print("\nRequest payload:")
    print(json.dumps(data, indent=2))
    
    response = requests.post(url, headers=headers, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))
    
if __name__ == "__main__":
    test_router() 