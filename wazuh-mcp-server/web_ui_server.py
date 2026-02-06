import sys
import os

# Add local site-packages to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-packages"))

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import json
import httpx
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from wazuh_mcp_server.api.wazuh_client import WazuhClient
from wazuh_mcp_server.config import WazuhConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wazuh AI Security Agent Web UI")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wazuh Client
wazuh_client = None

# Initialize Wazuh client on startup
@app.on_event("startup")
async def startup_event():
    global wazuh_client
    try:
        # Load config from environment variables
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
        
        wazuh_client = WazuhClient(config)
        await wazuh_client.initialize()
        logger.info("Wazuh client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Wazuh client: {e}")

# Tool definitions for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_agents",
            "description": "获取 Wazuh Agent 列表，支持按状态过滤",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "disconnected", "never_connected", "pending", "all"],
                        "description": "Agent 状态过滤"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回的最大数量",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_agent_info",
            "description": "获取指定 Agent 的详细信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID (例如: '001')"
                    }
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_vulnerabilities",
            "description": "获取 Agent 的漏洞信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["Critical", "High", "Medium", "Low"],
                        "description": "漏洞严重程度过滤"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "required": ["agent_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_alerts",
            "description": "获取最近的安全告警",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {
                        "type": "string",
                        "description": "最低告警级别 (例如: '10' 或 '12')"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10
                    }
                },
                "required": []
            }
        }
    }
]

async def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
    """Execute Wazuh tool and return result as string."""
    try:
        if tool_name == "get_agents":
            # Wazuh API requires status in ['active','pending','never_connected','disconnected'] or omit; never send empty string
            status = args.get("status") or "active"
            limit = args.get("limit", 10)
            if status == "all":
                status = None  # omit status to get all
            elif status not in ("active", "pending", "never_connected", "disconnected"):
                status = "active"
            result = await wazuh_client.get_agents(status=status, limit=limit)
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        elif tool_name == "get_agent_info":
            agent_id = args.get("agent_id")
            # Use search query for better compatibility
            result = await wazuh_client.get_agents(q=f"id={agent_id}")
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        elif tool_name == "get_vulnerabilities":
            agent_id = args.get("agent_id")
            severity = args.get("severity")
            limit = args.get("limit", 10)
            result = await wazuh_client.get_vulnerabilities(agent_id=agent_id, severity=severity, limit=limit)
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        elif tool_name == "get_alerts":
            level = args.get("level")
            limit = args.get("limit", 10)
            result = await wazuh_client.get_alerts(level=level, limit=limit)
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        else:
            return f"Error: Unknown tool {tool_name}"
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return f"Error executing {tool_name}: {str(e)}"

class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-chat"

@app.post("/api/chat")
async def chat_endpoint(
    request: ChatRequest, 
    x_api_key: str = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key required")

    async def generate():
        client = httpx.AsyncClient(timeout=60.0)
        messages = [
            {"role": "system", "content": "你是一个专业的安全运营专家(SOC Analyst)，负责管理和监控 Wazuh 安全平台。你可以使用工具来查询系统状态、Agent 信息、漏洞和告警。请根据工具返回的数据，用专业、简洁的中文回答用户问题。"},
            {"role": "user", "content": request.message}
        ]

        try:
            # First LLM call to get tool calls
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {x_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": request.model,
                    "messages": messages,
                    "tools": TOOLS,
                    "stream": False  # Use non-streaming for tool decision
                }
            )
            
            if response.status_code != 200:
                error_content = response.text
                logger.error(f"DeepSeek API Error: {response.status_code} - {error_content}")
                yield f"data: {json.dumps({'choices': [{'delta': {'content': f'Error: DeepSeek API returned {response.status_code} - {error_content}'}}]})}\n\n"
                return

            response_data = response.json()
            message = response_data["choices"][0]["message"]
            
            # Check for tool calls
            if "tool_calls" in message:
                tool_calls = message["tool_calls"]
                messages.append(message)  # Add assistant's response with tool calls
                
                # Execute tools
                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    
                    # Fix f-string backslash issue by defining message first
                    msg = f"\n*正在执行工具: {function_name}...*\n\n"
                    yield f"data: {json.dumps({'choices': [{'delta': {'content': msg}}]})}\n\n"
                    
                    tool_result = await execute_tool(function_name, arguments)
                    
                    # Filter out potential DSML garbage if tool execution failed messily
                    # (Simple heuristic: if result starts with Error and is very long)
                    if tool_result.startswith("Error") and len(tool_result) > 500:
                        tool_result = "Tool execution failed. Please check logs."

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result
                    })

                # Second LLM call with tool results (Streaming)
                async with client.stream(
                    "POST",
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {x_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": request.model,
                        "messages": messages,
                        "stream": True
                    }
                ) as stream_response:
                    async for chunk in stream_response.aiter_bytes():
                        # Filter out DSML tokens if they appear in the stream
                        try:
                            chunk_str = chunk.decode("utf-8")
                            if "< | DSML |" in chunk_str:
                                continue
                            yield chunk
                        except Exception:
                            yield chunk

            else:
                # No tool calls, just stream the content directly
                yield f"data: {json.dumps({'choices': [{'delta': {'content': message['content']}}]})}\n\n"
                yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield f"data: {json.dumps({'choices': [{'delta': {'content': f'Internal Error: {str(e)}'}}]})}\n\n"
        finally:
            await client.aclose()

    return StreamingResponse(generate(), media_type="text/event-stream")

# Serve static files
app.mount("/", StaticFiles(directory="web-ui", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use port 8001 to avoid conflicts
    uvicorn.run(app, host="0.0.0.0", port=8001)
