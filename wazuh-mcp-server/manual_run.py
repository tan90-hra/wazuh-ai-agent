import sys
import os
import asyncio
import json
from dotenv import load_dotenv

# Add libs to path
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_path = os.path.join(current_dir, "libs")
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

# Add src to path
src_path = os.path.join(current_dir, "src")
sys.path.insert(0, src_path)

from wazuh_mcp_server.config import WazuhConfig
from wazuh_mcp_server.api.wazuh_client import WazuhClient

# Load env
load_dotenv(os.path.join(current_dir, ".env"))

async def main():
    print("Initializing Wazuh Client...")
    config = WazuhConfig(
        wazuh_host=os.getenv("WAZUH_HOST", "https://127.0.0.1"),
        wazuh_user=os.getenv("WAZUH_USER", "wazuh"),
        wazuh_pass=os.getenv("WAZUH_PASS", "wazuh"),
        wazuh_port=int(os.getenv("WAZUH_PORT", 55000)),
        verify_ssl=os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true"
    )
    
    client = WazuhClient(config)
    try:
        await client.initialize()
        
        print("\n=== Online Agents ===")
        try:
            agents = await client.get_running_agents()
            print(json.dumps(agents, indent=2))
        except Exception as e:
            print(f"Error fetching agents: {e}")
        
        print("\n=== Security Posture Report ===")
        try:
            report = await client.generate_security_report(report_type="daily", include_recommendations=True)
            print(json.dumps(report, indent=2))
        except Exception as e:
            print(f"Error generating report: {e}")
            
    except Exception as e:
        print(f"Initialization Error: {e}")
    finally:
        if hasattr(client, "close"):
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
