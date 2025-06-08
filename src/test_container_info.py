import json
from discovery.podman_manager import PodmanManager
from datetime import datetime

def save_to_file(data: dict, filename: str):
    """Save data to a JSON file with proper formatting"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nData saved to {filename}")
    except Exception as e:
        print(f"\nError saving data: {e}")

def main():
    print("\n=== Starting Container Network Info Test ===")
    
    try:
        # Initialize PodmanManager
        print("Initializing PodmanManager...")
        podman = PodmanManager(data_dir="podman_data")
        
        # Get network information
        print("Fetching container network information...")
        network_info = podman.get_container_network_info()
        
        # Save the data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"container_info_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "containers": network_info
        }
        
        # Print summary
        print("\n=== Container Network Information Summary ===")
        print(f"Total containers found: {len(network_info)}")
        
        if network_info:
            print("\nContainer Details:")
            for container in network_info:
                print(f"\nContainer: {container.get('name', 'Unknown')}")
                print(f"  Status: {container.get('status', 'Unknown')}")
                print(f"  IP Address: {container.get('ip_address', 'Unknown')}")
                print("  Ports:")
                for port, mappings in container.get('ports', {}).items():
                    for mapping in mappings:
                        print(f"    {mapping.get('HostIp', '0.0.0.0')}:{port} -> {mapping.get('ContainerPort', 'Unknown')}")
        else:
            print("\nNo containers found.")
        
        # Save to file
        save_to_file(output_data, filename)
        print("\n=== Test completed successfully ===")
        
    except Exception as e:
        print(f"\nError during execution: {e}")

if __name__ == "__main__":
    main() 