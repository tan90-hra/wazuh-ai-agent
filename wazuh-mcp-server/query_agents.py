import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

from wazuh_mcp_server.config import WazuhConfig
from wazuh_mcp_server.api.wazuh_client import WazuhClient

# Load env
load_dotenv(os.path.join(current_dir, ".env"))

async def main():
    print("Initializing Wazuh Client...")
    
    config = WazuhConfig(
        wazuh_host=os.getenv("WAZUH_HOST"),
        wazuh_user=os.getenv("WAZUH_USER"),
        wazuh_pass=os.getenv("WAZUH_PASS"),
        wazuh_port=int(os.getenv("WAZUH_PORT", 55000)),
        verify_ssl=os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true"
    )
    
    client = WazuhClient(config)
    try:
        await client.initialize()
        
        print("\n=== Online Agents ===")
        try:
            agents = await client.get_running_agents()
            # Wazuh response usually has format {"data": {"affected_items": [...]}} or similar
            # We will just print the full JSON for clarity
            print(json.dumps(agents, indent=2))
        except Exception as e:
            print(f"Error fetching online agents: {e}")

        print("\n=== Agent 001 Details ===")
        try:
            # Try to get specific agent info. 
            # In Wazuh API, passing agents_list filters by ID
            agent_details = await client.get_agents(agents_list="001")
            print(json.dumps(agent_details, indent=2))
        except Exception as e:
            print(f"Error fetching agent 001: {e}")
            
    except Exception as e:
        print(f"Initialization Error: {e}")
    finally:
        if hasattr(client, "close"):
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
