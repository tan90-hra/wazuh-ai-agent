# Wazuh AI-SOC Agent (MCP Server)

This project implements an AI-SOC Agent using the Model Context Protocol (MCP) to connect Wazuh with LLMs (like Cursor/Claude).

## Prerequisites

1.  **Python 3.10+**
2.  **Wazuh Environment** (Server & Indexer) accessible from this machine.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Edit `.env` file to match your Wazuh settings.
    *   If Wazuh is in a VM, ensure you have **Port Forwarding** enabled:
        *   Forward Host Port `55000` -> VM Port `55000` (Wazuh API)
        *   Forward Host Port `9200` -> VM Port `9200` (Wazuh Indexer)
    *   Update URLs in `.env` if using different IPs/Ports.

## Running the Server

Run the MCP server locally:

```bash
python server.py
```

## Using with Cursor

To use this Agent in Cursor:

1.  Go to **Cursor Settings** > **MCP**.
2.  Add a new MCP server:
    *   **Name**: `wazuh-agent`
    *   **Type**: `command`
    *   **Command**: `python c:\Users\Administrator\Desktop\数据安全治理\Fedavg作业\AI-SOC-Agent\server.py`

## Features

*   `fetch_agents`: List all Wazuh agents.
*   `fetch_alerts`: Search security alerts (e.g., "SSH brute force").
*   `trigger_block_ip`: Block an IP on a specific agent (Active Response).
