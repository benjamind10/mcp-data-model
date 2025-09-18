# mcp_server/server.py

from fastapi import FastAPI, Query, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import logging
from mcp_server.broker import get_tags_from_server, generate_model_prompt
from mcp_server.prompt_tools import generate_prompt_from_tags
from mcp_server.tool_registry import TOOL_REGISTRY
from opcua_client import MCPClient

# Logger
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s - %(message)s"))
logger.addHandler(handler)

app = FastAPI(
    title="MCP Server",
    description="Model Control Plane API for browsing and retrieving OPC UA data",
    version="0.1.0",
)

# Known OPC UA servers
KNOWN_SERVERS = [
    "opc.tcp://localhost:4840",
    "opc.tcp://localhost:4841",
    "opc.tcp://localhost:4842",
]


class ServerList(BaseModel):
    servers: List[str]
    skip_system_tags: bool = True


@app.get("/")
def health() -> Dict[str, Any]:
    return {"ok": True, "name": "MCP Server", "version": "0.1.0"}


@app.get("/servers")
def list_servers() -> List[str]:
    return KNOWN_SERVERS


@app.get("/tags")
def get_tags(server_url: str = Query(...), skip_system_tags: bool = True):
    try:
        tags = get_tags_from_server(server_url, skip_system_tags=skip_system_tags)
        return tags
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tags/batch")
def get_tags_batch(data: ServerList):
    all_tags = []
    for url in data.servers:
        try:
            tags = get_tags_from_server(url, skip_system_tags=data.skip_system_tags)
            all_tags.extend(tags)
        except Exception as e:
            all_tags.append({"server_url": url, "error": str(e)})
    return all_tags


@app.get("/value")
def read_tag_value(server_url: str = Query(...), node_id: str = Query(...)):
    try:
        client = MCPClient([server_url])
        client.connect_all()
        value = client.read_node(server_url, node_id)
        client.disconnect_all()
        return {"value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prompt")
def get_prompt(server_url: str = Query(...), skip_system_tags: bool = True):
    try:
        prompt = generate_model_prompt(server_url, skip_system_tags=skip_system_tags)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prompt/batch")
def get_prompt_batch(data: ServerList):
    try:
        all_tags = []
        for url in data.servers:
            tags = get_tags_from_server(url, skip_system_tags=data.skip_system_tags)
            all_tags.extend(tags)
        prompt = generate_prompt_from_tags(all_tags)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/registry")
def get_registry():
    return TOOL_REGISTRY


# MCP endpoint
@app.post("/")
async def mcp_entry(request: Request):
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload must be an object")

    # Handle JSON-RPC
    if "jsonrpc" in payload and "method" in payload:
        method = payload["method"]
        params = payload.get("params", {})
        id = payload.get("id")

        if method == "initialize":
            result = {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "MCP Server", "version": "0.1.0"},
            }
            return {"jsonrpc": "2.0", "id": id, "result": result}

        elif method == "tools/list":
            tools = []
            for t in TOOL_REGISTRY.get("tools", []):
                tools.append(
                    {
                        "name": t["name"],
                        "description": t["description"],
                        "inputSchema": t["input_schema"],
                    }
                )
            return {"jsonrpc": "2.0", "id": id, "result": {"tools": tools}}

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "get_tags":
                server_url = arguments.get("server_url")
                skip_system_tags = arguments.get("skip_system_tags", True)
                tags = get_tags_from_server(
                    server_url, skip_system_tags=skip_system_tags
                )
                return {"jsonrpc": "2.0", "id": id, "result": {"tags": tags}}

            elif tool_name == "get_tags_batch":
                servers = arguments.get("servers", [])
                skip_system_tags = arguments.get("skip_system_tags", True)
                all_tags = []
                for url in servers:
                    try:
                        tags = get_tags_from_server(
                            url, skip_system_tags=skip_system_tags
                        )
                        all_tags.extend(tags)
                    except Exception as e:
                        all_tags.append({"server_url": url, "error": str(e)})
                return {"jsonrpc": "2.0", "id": id, "result": {"tags": all_tags}}

            elif tool_name == "generate_prompt":
                server_url = arguments.get("server_url")
                skip_system_tags = arguments.get("skip_system_tags", True)
                prompt = generate_model_prompt(
                    server_url, skip_system_tags=skip_system_tags
                )
                return {"jsonrpc": "2.0", "id": id, "result": {"prompt": prompt}}

            elif tool_name == "generate_prompt_batch":
                servers = arguments.get("servers", [])
                skip_system_tags = arguments.get("skip_system_tags", True)
                all_tags = []
                for url in servers:
                    tags = get_tags_from_server(url, skip_system_tags=skip_system_tags)
                    all_tags.extend(tags)
                prompt = generate_prompt_from_tags(all_tags)
                return {"jsonrpc": "2.0", "id": id, "result": {"prompt": prompt}}

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool '{tool_name}' not found",
                    },
                }

        else:
            return {
                "jsonrpc": "2.0",
                "id": id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

    # Handle direct tool calls (for compatibility)
    tool_name = payload.get("tool") or payload.get("name")
    arguments = (
        payload.get("input") or payload.get("args") or payload.get("arguments") or {}
    )

    if tool_name == "initialize":
        result = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {"listChanged": True}},
            "serverInfo": {"name": "MCP Server", "version": "0.1.0"},
        }
        return result

    elif tool_name == "tools/list":
        tools = []
        for t in TOOL_REGISTRY.get("tools", []):
            tools.append(
                {
                    "name": t["name"],
                    "description": t["description"],
                    "inputSchema": t["input_schema"],
                }
            )
        return {"tools": tools}

    elif tool_name == "get_tags":
        server_url = arguments.get("server_url")
        skip_system_tags = arguments.get("skip_system_tags", True)
        tags = get_tags_from_server(server_url, skip_system_tags=skip_system_tags)
        return {"tags": tags}

    elif tool_name == "get_tags_batch":
        servers = arguments.get("servers", [])
        skip_system_tags = arguments.get("skip_system_tags", True)
        all_tags = []
        for url in servers:
            try:
                tags = get_tags_from_server(url, skip_system_tags=skip_system_tags)
                all_tags.extend(tags)
            except Exception as e:
                all_tags.append({"server_url": url, "error": str(e)})
        return {"tags": all_tags}

    elif tool_name == "generate_prompt":
        server_url = arguments.get("server_url")
        skip_system_tags = arguments.get("skip_system_tags", True)
        prompt = generate_model_prompt(server_url, skip_system_tags=skip_system_tags)
        return {"prompt": prompt}

    elif tool_name == "generate_prompt_batch":
        servers = arguments.get("servers", [])
        skip_system_tags = arguments.get("skip_system_tags", True)
        all_tags = []
        for url in servers:
            tags = get_tags_from_server(url, skip_system_tags=skip_system_tags)
            all_tags.extend(tags)
        prompt = generate_prompt_from_tags(all_tags)
        return {"prompt": prompt}

    else:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
