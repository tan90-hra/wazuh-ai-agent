import asyncio
import sys
import os
import types

# Mock fastapi if missing
try:
    import fastapi
except ImportError:
    print("fastapi not found, mocking...")
    mock_fastapi = types.ModuleType("fastapi")
    class HTTPException(Exception):
        def __init__(self, status_code, detail=None, headers=None):
            self.status_code = status_code
            self.detail = detail
            self.headers = headers
    mock_fastapi.HTTPException = HTTPException
    sys.modules["fastapi"] = mock_fastapi
    
    # Also mock fastapi.responses if needed (server.py uses it)
    mock_responses = types.ModuleType("fastapi.responses")
    mock_responses.StreamingResponse = object
    mock_responses.JSONResponse = object
    sys.modules["fastapi.responses"] = mock_responses

    # Mock fastapi.middleware.cors
    mock_cors = types.ModuleType("fastapi.middleware.cors")
    mock_cors.CORSMiddleware = object
    sys.modules["fastapi.middleware.cors"] = mock_cors

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from wazuh_mcp_server.api.wazuh_client import WazuhClient
from wazuh_mcp_server.config import WazuhConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Configuration from .env or hardcoded for testing
    # Using values confirmed working for API
    config = WazuhConfig(
        wazuh_host="192.168.88.129",
        wazuh_user="wazuh",
        wazuh_pass="fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO",
        wazuh_port=55000,
        verify_ssl=False,
        # Indexer config - updated to 9201
        wazuh_indexer_host="192.168.88.129",
        wazuh_indexer_port=9201,
        wazuh_indexer_user="admin", 
        wazuh_indexer_pass="Hra010809." 
    )

    client = WazuhClient(config)
    
    try:
        print("Initializing client...")
        await client.initialize()
        print("Client initialized.")

        # Test Indexer Connectivity explicitly
        if client._indexer_client:
            print("\n--- Testing Wazuh Indexer Connectivity ---")
            try:
                # Try a simple health check or version check if available, or just a search
                # Since get_vulnerability_summary is simple, let's try that or just assume initialize worked if no error
                # But let's try to fetch something that requires indexer
                print("Attempting to fetch vulnerability summary (requires Indexer)...")
                vuln_summary = await client.get_vulnerability_summary(time_range="1d")
                print("Indexer connection successful!")
                import json
                print(json.dumps(vuln_summary, indent=2))
            except Exception as e:
                print(f"Indexer connection failed: {e}")
        else:
            print("Indexer client not initialized.")
        
        print("\n--- Listing Online Agents ---")
        agents_data = await client.get_agents(status="active", limit=10)
        
        if agents_data and 'items' in agents_data:
            print(f"Found {len(agents_data['items'])} active agents.")
            for agent in agents_data['items']:
                print(f"ID: {agent.get('id')} | Name: {agent.get('name')} | IP: {agent.get('ip')} | Status: {agent.get('status')}")
        else:
            print("No active agents found or invalid response format.")
            print(agents_data)

        print("\n--- Querying Agent 001 Details (Attempt 1: Path) ---")
        try:
            # Try accessing via path /agents/001
            agent_001 = await client._request("GET", "/agents/001")
            import json
            print(json.dumps(agent_001, indent=2))
        except Exception as e:
            print(f"Path attempt failed: {e}")

        print("\n--- Querying Agent 001 Details (Attempt 2: Search Query) ---")
        try:
            # Try accessing via q=id=001
            agent_001 = await client.get_agents(q="id=001")
            import json
            print(json.dumps(agent_001, indent=2))
        except Exception as e:
            print(f"Query attempt failed: {e}")

        print("\n--- Checking Vulnerabilities for Agent 001 ---")
        try:
            vulns = await client.get_vulnerabilities(agent_id="001", limit=5)
            import json
            print(json.dumps(vulns, indent=2))
        except Exception as e:
            print(f"Vulnerability check failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
