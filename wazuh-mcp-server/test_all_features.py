import asyncio
import sys
import os
import json
import logging

# Add local site-packages to path
sys.path.append(os.path.join(os.getcwd(), "site-packages"))
# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from wazuh_mcp_server.api.wazuh_client import WazuhClient
from wazuh_mcp_server.config import WazuhConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_tool(name, func, **kwargs):
    print(f"\nTesting {name}...")
    try:
        result = await func(**kwargs)
        # Check if result is valid JSON-serializable
        json.dumps(result)
        print(f"PASS: {name}")
        return True
    except Exception as e:
        print(f"FAIL: {name} - {e}")
        return False

async def main():
    # Load config from environment variables or hardcoded for test
    from dotenv import load_dotenv
    load_dotenv()
    
    config = WazuhConfig(
        wazuh_host=os.getenv("WAZUH_HOST", "192.168.88.129"),
        wazuh_user=os.getenv("WAZUH_USER", "wazuh"),
        wazuh_pass=os.getenv("WAZUH_PASS", "fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO"),
        wazuh_port=int(os.getenv("WAZUH_PORT", "55000")),
        verify_ssl=os.getenv("WAZUH_VERIFY_SSL", "false").lower() == "true",
        wazuh_indexer_host=os.getenv("WAZUH_INDEXER_HOST", "192.168.88.129"),
        wazuh_indexer_port=int(os.getenv("WAZUH_INDEXER_PORT", "9201")),
        wazuh_indexer_user=os.getenv("WAZUH_INDEXER_USER", "admin"),
        wazuh_indexer_pass=os.getenv("WAZUH_INDEXER_PASSWORD", "Hra010809.")
    )

    client = WazuhClient(config)
    
    try:
        print("Initializing client...")
        await client.initialize()
        print("Client initialized.")

        # 1. Test get_agents
        await test_tool("get_agents", client.get_agents, status="active", limit=5)

        # 2. Test get_vulnerabilities (Requires Indexer)
        await test_tool("get_vulnerabilities", client.get_vulnerabilities, agent_id="001", limit=5)

        # 3. Test get_alerts (Requires Indexer & Code Fix)
        # This will fail if get_alerts calls /alerts endpoint
        await test_tool("get_alerts", client.get_alerts, level="3", limit=5)

        # 4. Test get_agent_info (via get_agents)
        await test_tool("get_agent_info", client.get_agents, q="id=001")

        # 5. Test search_security_events
        await test_tool("search_security_events", client.search_security_events, query="agent.id:001", time_range="24h", limit=5)

        # 6. Test get_manager_info
        await test_tool("get_manager_info", client.get_manager_info)

    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
