import json
import logging
import subprocess
import os
import platform
from typing import Dict, List, Any

class PodmanManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Multiple checks to detect if we're running in a container
        self.is_container = any([
            os.path.exists('/.containerenv'),
            os.path.exists('/.dockerenv'),
            os.getenv('CONTAINER') == 'true',
            os.path.exists('/run/podman/podman.sock')  # Check if podman socket is mounted
        ])
        
        if self.is_container:
            self.logger.info("Running in container mode")
        else:
            self.logger.info("Running in local mode")
    
    def _get_default_connection(self) -> str:
        """Get the default connection name based on the platform"""
        try:
            # Run podman system connection list and parse the output
            result = subprocess.run(
                ["podman", "system", "connection", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            connections = json.loads(result.stdout)
            
            # Find the default connection (usually has "Default": true)
            for conn in connections:
                if conn.get("Default", False):
                    return conn.get("Name", "")
            
            # If no default found, return the first root connection
            for conn in connections:
                if "root" in conn.get("Name", "").lower():
                    return conn.get("Name", "")
            
            # If still no connection found, return the first one
            if connections:
                return connections[0].get("Name", "")
            
        except Exception as e:
            self.logger.warning(f"Failed to get default connection: {e}")
        
        # Fallback to platform-specific defaults
        system = platform.system()
        if system == "Windows":
            return "podman-machine-default-root"
        elif system == "Darwin":  # macOS
            return "podman-machine-default"  # macOS typically doesn't need root
        return ""
    
    def execute_podman_command(self, command: List[str]) -> tuple[str, str]:
        """Execute a Podman command and return its output"""
        try:
            if self.is_container:
                # In container mode, use the socket directly
                full_command = ["podman", "--remote"] + command
            elif platform.system() in ["Windows", "Darwin"]:
                # On Windows/macOS, explicitly specify the connection
                connection = self._get_default_connection()
                if connection:
                    full_command = ["podman", "--remote", "--connection", connection] + command
                else:
                    full_command = ["podman", "--remote"] + command
            else:
                full_command = ["podman"] + command
            
            # Execute the command
            process = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=True
            )
            if process.stderr:
                self.logger.warning(f"Command stderr: {process.stderr.strip()}")
            return process.stdout.strip(), process.stderr.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to execute podman command: {e}")
            self.logger.error(f"Command failed with output: {e.stderr}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error executing podman command: {str(e)}")
            raise

    def get_container_network_info(self) -> List[Dict[str, Any]]:
        """Get network information for all containers"""
        try:
            # Get list of containers
            stdout, _ = self.execute_podman_command(["ps", "-a", "--format", "json"])
            containers = json.loads(stdout) if stdout else []
            
            network_info = []
            for container in containers:
                container_id = container.get("Id", "")
                
                # Get detailed container info
                inspect_output, _ = self.execute_podman_command(["inspect", container_id])
                inspect_data = json.loads(inspect_output)[0]
                
                network_settings = inspect_data.get("NetworkSettings", {})
                ports = network_settings.get("Ports", {})
                networks = network_settings.get("Networks", {})
                
                # Format container network information for agent discovery
                container_info = {
                    "container_id": container_id,
                    "name": container.get("Names", [""])[0],
                    "status": container.get("Status", ""),
                    "ip_address": next(iter(networks.values()), {}).get("IPAddress", ""),
                    "ports": ports,
                    "created": container.get("Created", ""),
                    "network_mode": network_settings.get("NetworkMode", "")
                }
                network_info.append(container_info)
            
            return network_info
            
        except Exception as e:
            self.logger.error(f"Error getting container network info: {e}", exc_info=True)
            return [] 

    def get_agent_info_from_containers(self) -> Dict[str, Dict[str, Any]]:
        """Get information about agent containers.
        
        Returns:
            A dictionary with agent information in the format:
            {
                'agents': {
                    'name': {
                        'container_id': str,
                        'name': str,
                        'container_ip': str,  # Format: "http://IP:PORT"
                        'exposed_ip': str,   # Format: "http://localhost:PORT" or "http://IP:PORT"
                        'is_running': bool,
                        'status': str,
                        'capabilities': str  # From container label
                    },
                    ...
                }
            }
        """
        try:
            containers = self.get_container_network_info()
            agents = {}
            
            for container in containers:
                name = container.get('name', '')
                if 'agent' in name.lower():
                    # Check if container is running based on status
                    status = container.get('status', '').lower()
                    is_running = 'up' in status and 'exited' not in status
                    
                    # Get container details including labels
                    container_id = container.get('container_id', '')
                    inspect_output, _ = self.execute_podman_command(["inspect", container_id])
                    inspect_data = json.loads(inspect_output)[0]
                    capabilities = inspect_data.get('Config', {}).get('Labels', {}).get('capabilities', '')
                    
                    # Get the first port mapping
                    container_ip = container.get('ip_address', '')
                    ports = container.get('ports', {})
                    port = ''
                    exposed_ip = ''
                    
                    # Look through port mappings to find the host port
                    for container_port, mappings in ports.items():
                        if mappings and isinstance(mappings, list) and len(mappings) > 0:
                            mapping = mappings[0]
                            port = mapping.get('HostPort', '')
                            host_ip = mapping.get('HostIp', '0.0.0.0')
                            if port:
                                # Use 'localhost' if the host IP is 0.0.0.0
                                exposed_ip = f"http://localhost:{port}" if host_ip == '0.0.0.0' else f"http://{host_ip}:{port}"
                                break
                    
                    # Combine IP and port if both exist
                    if container_ip and port:
                        container_ip = f"http://{container_ip}:{port}"
                    
                    agents[name] = {
                        'container_id': container_id,
                        'name': name,
                        'container_ip': container_ip,
                        'exposed_ip': exposed_ip,
                        'is_running': is_running,
                        'status': container.get('status', ''),
                        'capabilities': capabilities
                    }
            
            return {'agents': agents}
            
        except Exception as e:
            self.logger.error(f"Error getting agent container info: {e}")
            return {'agents': {}} 