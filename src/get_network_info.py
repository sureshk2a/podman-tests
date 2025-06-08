from discovery.podman_manager import PodmanManager
import json
def main():
    # Initialize PodmanManager
    podman = PodmanManager()
    
    # Get network information for all containers
    network_info = podman.get_container_network_info()
    
    # Print the network information in a readable format
    for container in network_info:
       print(json.dumps(container, indent=4))

if __name__ == "__main__":
    main() 