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
        # Indexer config - might be incorrect but we try running agents first
        wazuh_indexer_host="192.168.88.129",
        wazuh_indexer_port=9200,
        wazuh_indexer_user="admin", 
        wazuh_indexer_pass="MiDM7x98.DoQHkJ07p.8YdPCBbRfVzFc" # Trying default first
    )

    client = WazuhClient(config)
    
    try:
        print("Initializing client...")
        await client.initialize()
        print("Client initialized.")
        
        print("\n--- Listing Online Agents ---")
        agents_data = await client.get_agents(status="active", limit=10)
        
        if agents_data and 'items' in agents_data:
            print(f"Found {len(agents_data['items'])} active agents.")
            for agent in agents_data['items']:
                print(f"ID: {agent.get('id')} | Name: {agent.get('name')} | IP: {agent.get('ip')} | Status: {agent.get('status')}")
        else:
            print("No active agents found or invalid response format.")
            print(agents_data)

        print("\n--- Querying Agent 001 Details ---")
        agent_001 = await client.get_agents(agent_id="001")
        if agent_001 and 'items' in agent_001 and len(agent_001['items']) > 0:
            import json
            print(json.dumps(agent_001['items'][0], indent=2))
        else:
            print("Agent 001 not found.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
