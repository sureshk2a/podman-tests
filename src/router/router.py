import asyncio
import httpx
import json
import logging
import os
import sys
from collections.abc import AsyncGenerator
from typing import Optional
from datetime import datetime

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server
from discovery.podman_manager import PodmanManager
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Get log level from environment variable or default to WARNING
log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()

# Configure root logger with a stdout handler
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, log_level))

# Remove any existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add stdout handler with a simpler format
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s | %(message)s')
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(getattr(logging, log_level))
root_logger.addHandler(stdout_handler)

# Force immediate output
sys.stdout.flush()

# Get logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level))

# Create and configure the server
server = Server()

# Ensure PodmanManager logger inherits our configuration
podman_logger = logging.getLogger("PodmanManager")
podman_logger.handlers = []  # Remove any existing handlers
podman_logger.propagate = True  # Ensure it propagates to root logger
podman_logger.setLevel(getattr(logging, log_level))

@server.agent()
async def router(
    input: str, context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Router that checks container status and makes API requests"""
    try:    
        logger.info("Starting agent info request...")
        podman = PodmanManager()
 
        agent_info = podman.get_agent_info_from_containers()
        yield Message(parts=[MessagePart(content=json.dumps(agent_info, indent=4), content_type="application/json")])
  
    except Exception as e:
        logger.error(f"Error getting agent info: {e}", exc_info=True)
        yield Message(parts=[MessagePart(content=f"Error: {str(e)}", content_type="text/plain")])

server.run(host="0.0.0.0", port=8001) 