import os

file_path = r"c:\Users\Administrator\Desktop\数据安全治理\Fedavg作业\AI-SOC-Agent\wazuh-mcp-server\src\wazuh_mcp_server\api\wazuh_client.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_code = """    async def get_alerts(self, **params) -> Dict[str, Any]:
        \"\"\"Get alerts from Wazuh.\"\"\"
        return await self._request("GET", "/alerts", params=params)"""

new_code = """    async def get_alerts(self, **params) -> Dict[str, Any]:
        \"\"\"Get alerts from Wazuh Indexer.\"\"\"
        if not self._indexer_client:
            raise IndexerNotConfiguredError("Wazuh Indexer is required for querying alerts.")
            
        level = params.get("level")
        limit = params.get("limit", 10)
        
        return await self._indexer_client.get_alerts(level=level, limit=limit)"""

if old_code in content:
    new_content = content.replace(old_code, new_code)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated wazuh_client.py")
else:
    print("Could not find the target code block. Here is a snippet of the file:")
    print(content[3000:4000]) # Print a chunk where get_alerts likely is
