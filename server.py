import os
import json
import base64
import requests
import urllib3
from typing import Optional, List, Dict, Any
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Configuration
WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://127.0.0.1:55000")
WAZUH_API_USER = os.getenv("WAZUH_API_USER", "wazuh")
WAZUH_API_PASSWORD = os.getenv("WAZUH_API_PASSWORD", "wazuh")
WAZUH_INDEXER_URL = os.getenv("WAZUH_INDEXER_URL", "https://127.0.0.1:9200")
WAZUH_INDEXER_USER = os.getenv("WAZUH_INDEXER_USER", "admin")
WAZUH_INDEXER_PASSWORD = os.getenv("WAZUH_INDEXER_PASSWORD", "admin")

# Initialize MCP Server
mcp = FastMCP("Wazuh AI-SOC Agent")

class WazuhClient:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
        self.session.verify = False
    
    def authenticate(self):
        """Get JWT token from Wazuh API"""
        auth_url = f"{WAZUH_API_URL}/security/user/authenticate"
        try:
            response = self.session.post(
                auth_url, 
                auth=(WAZUH_API_USER, WAZUH_API_PASSWORD),
                timeout=10
            )
            response.raise_for_status()
            self.token = response.json()['data']['token']
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def get_agents(self):
        """Get list of agents"""
        if not self.token:
            self.authenticate()
        
        try:
            response = self.session.get(f"{WAZUH_API_URL}/agents?pretty=true&select=id,name,ip,status")
            response.raise_for_status()
            data = response.json().get('data', {})
            return data.get('affected_items', [])
        except Exception as e:
            return f"Error fetching agents: {e}"

    def active_response(self, agent_id: str, command: str, arguments: list = None):
        """Trigger active response on an agent"""
        if not self.token:
            self.authenticate()
            
        data = {
            "command": command,
            "custom": False,
            "alert": {
                "data": {
                    "srcip": arguments[0] if arguments else "0.0.0.0" 
                }
            }
        }
        
        # Note: This is a simplified active response call. 
        # Real Wazuh AR requires specific payload structures usually matching the command.
        # For 'firewall-drop', it usually expects 'srcip'.
        
        try:
            # Check available AR commands first to map correctly
            # This is a placeholder for the actual AR endpoint logic
            # PUT /active-response?agents_list=001
            url = f"{WAZUH_API_URL}/active-response?agents_list={agent_id}"
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return f"Error triggering active response: {e}"

client = WazuhClient()

@mcp.tool()
def fetch_agents() -> str:
    """Fetch the list of connected Wazuh agents and their status."""
    agents = client.get_agents()
    return json.dumps(agents, indent=2)

@mcp.tool()
def fetch_alerts(query: str = "*", limit: int = 10) -> str:
    """
    Fetch security alerts from Wazuh Indexer (Elasticsearch).
    Args:
        query: Lucene query string (default: "*")
        limit: Number of alerts to return (default: 10)
    """
    # Direct query to Indexer
    url = f"{WAZUH_INDEXER_URL}/wazuh-alerts-*/_search"
    payload = {
        "query": {
            "query_string": {
                "query": query
            }
        },
        "size": limit,
        "sort": [{"timestamp": "desc"}]
    }
    
    try:
        response = requests.get(
            url,
            json=payload,
            auth=(WAZUH_INDEXER_USER, WAZUH_INDEXER_PASSWORD),
            verify=False,
            timeout=10
        )
        response.raise_for_status()
        hits = response.json().get('hits', {}).get('hits', [])
        alerts = [h['_source'] for h in hits]
        return json.dumps(alerts, indent=2)
    except Exception as e:
        return f"Error fetching alerts: {e}"

@mcp.tool()
def trigger_block_ip(agent_id: str, ip_address: str) -> str:
    """
    Trigger an active response to block an IP address on a specific agent.
    This simulates the 'host-deny' or 'firewall-drop' command.
    """
    # In a real scenario, you map this to the specific AR command name configured in Wazuh
    # E.g. 'firewall-drop' or 'host-deny'
    result = client.active_response(agent_id, "host-deny", [ip_address])
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
