# Podman Agent Discovery Demo

This repository demonstrates a system for managing and discovering Podman containers with a focus on agent discovery and network information. It includes:

- A router service for container discovery
- Sample agent containers
- Network information tracking
- Container health monitoring

## Prerequisites

### macOS Setup
1. Install Podman:
   ```bash
   brew install podman
   ```

2. Initialize Podman machine:
   ```bash
   podman machine init
   podman machine start
   ```

3. Set environment variable for socket location:
   ```bash
   # For macOS, the socket is typically located at:
   export PODMAN_SOCKET="$HOME/.podman/podman.sock"
   ```

### Linux/Windows Setup
- Install Podman using your system's package manager
- The socket location will be automatically detected

## Quick Demo

1. **Start the Services**
   ```bash
   # Start the router
   podman-compose up -d router

   # Start the agent
   cd agents && podman-compose up -d
   ```

2. **Check Agent Status**
   ```bash
   python src/router/client.py
   ```
   This will show:
   - Container IPs and exposed ports
   - Agent capabilities
   - Running status
   - Health information

## Architecture

The system consists of three main components:

1. **Router Service** (`src/router/`)
   - Discovers and tracks containers
   - Provides container network information
   - Exposes REST API for queries

2. **Agent Service** (`agents/`)
   - Sample agent implementation
   - Demonstrates container labeling
   - Shows network configuration

3. **Discovery System** (`src/discovery/`)
   - Container network information tracking
   - Health monitoring
   - Automatic IP and port management

## Features

- **Container Discovery**
  - Automatic detection of agent containers
  - Network information tracking
  - Health status monitoring

- **Network Management**
  - Internal container IPs (e.g., `http://10.89.1.2:8080`)
  - Exposed host endpoints (e.g., `http://localhost:8080`)
  - Port mapping and management

- **Agent Capabilities**
  - Container labeling for capability discovery
  - Automatic capability reporting
  - Health status tracking

## API Examples

1. **Get Agent Information**
   ```python
   # Using the client
   python src/router/client.py

   # Expected output:
   {
       "agents": {
           "podman-agent-instance": {
               "container_id": "f84fdf7b...",
               "name": "podman-agent-instance",
               "container_ip": "http://10.89.1.2:8080",
               "exposed_ip": "http://localhost:8080",
               "is_running": true,
               "status": "Up 2 minutes",
               "capabilities": "A sample agent that can process messages and respond"
           }
       }
   }
   ```

## Development Setup

1. **Prerequisites**
   - Python 3.8+
   - Podman
   - UV package manager

2. **Installation**
   ```bash
   # Install dependencies
   uv pip install -e .

   # For development
   uv pip install -e ".[dev]"
   ```

3. **Running Tests**
   ```bash
   python src/test_container_info.py
   python src/test_router.py
   ```

## Network Configuration

The system uses three Podman networks:
- `podman` (10.88.0.0/16) - Default Podman network
- `podman-tests_default` (10.89.0.0/24) - Router network
- `agents_default` (10.89.1.0/24) - Agent network

## Troubleshooting

1. **Container Not Found**
   - Check if containers are running: `podman ps`
   - Verify network settings: `podman network ls`
   - Check container logs: `podman logs <container-name>`

2. **Network Issues**
   - Verify port mappings: `podman port <container-name>`
   - Check network connectivity: `podman network inspect <network-name>`
   - Ensure router service is running: `podman-compose ps`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - Feel free to use and modify as needed. 