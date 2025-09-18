from .broker import get_tags_from_server, generate_model_prompt
from .prompt_tools import generate_prompt_from_tags


# Define handlers
async def get_tags_handler(args):
    server_url = args.get("server_url")
    if server_url and server_url.startswith("http://"):
        server_url = server_url.replace("http://", "opc.tcp://", 1)
    skip_system_tags = args.get("skip_system_tags", True)
    tags = get_tags_from_server(server_url, skip_system_tags=skip_system_tags)
    return tags


async def get_tags_batch_handler(args):
    servers = args.get("servers", [])
    skip_system_tags = args.get("skip_system_tags", True)
    all_tags = []
    for url in servers:
        if url and url.startswith("http://"):
            url = url.replace("http://", "opc.tcp://", 1)
        tags = get_tags_from_server(url, skip_system_tags=skip_system_tags)
        all_tags.extend(tags)
    return all_tags


async def generate_prompt_handler(args):
    server_url = args.get("server_url")
    if server_url and server_url.startswith("http://"):
        server_url = server_url.replace("http://", "opc.tcp://", 1)
    skip_system_tags = args.get("skip_system_tags", True)
    prompt = generate_model_prompt(server_url, skip_system_tags=skip_system_tags)
    return {"prompt": prompt}


async def generate_prompt_batch_handler(args):
    servers = args.get("servers", [])
    skip_system_tags = args.get("skip_system_tags", True)
    all_tags = []
    for url in servers:
        if url and url.startswith("http://"):
            url = url.replace("http://", "  opc.tcp://", 1)
        tags = get_tags_from_server(url, skip_system_tags=skip_system_tags)
        all_tags.extend(tags)
    prompt = generate_prompt_from_tags(all_tags)
    return {"prompt": prompt}


TOOL_REGISTRY = {
    "name": "MCP Data Modeling Tools",
    "version": "0.1.0",
    "description": "MCP server tools for discovering, modeling, and analyzing OPC UA servers using AI agents.",
    "contact": {"author": "Ben Duran", "email": "ben.duran@proton.me"},
    "base_url": "http://localhost:8000",  # Update if deployed
    "tools": [
        {
            "name": "get_tags",
            "endpoint": "/tags",
            "method": "POST",
            "description": "Returns all variable nodes from the specified OPC UA server.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "server_url": {"type": "string"},
                    "skip_system_tags": {"type": "boolean", "default": True},
                },
                "required": ["server_url"],
            },
            "output_schema": {"type": "array", "items": {"type": "object"}},
            "handler": get_tags_handler,
        },
        {
            "name": "get_tags_batch",
            "endpoint": "/tags/batch",
            "method": "POST",
            "description": "Fetch tags from multiple OPC UA servers.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "servers": {"type": "array", "items": {"type": "string"}},
                    "skip_system_tags": {"type": "boolean", "default": True},
                },
                "required": ["servers"],
            },
            "output_schema": {"type": "array", "items": {"type": "object"}},
            "handler": get_tags_batch_handler,
        },
        {
            "name": "generate_prompt",
            "endpoint": "/prompt",
            "method": "POST",
            "description": "Generates a modeling prompt from OPC UA server tags.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "server_url": {"type": "string"},
                    "skip_system_tags": {"type": "boolean", "default": True},
                },
                "required": ["server_url"],
            },
            "output_schema": {"type": "string"},
            "handler": generate_prompt_handler,
        },
        {
            "name": "generate_prompt_batch",
            "endpoint": "/prompt/batch",
            "method": "POST",
            "description": "Generates a modeling prompt from multiple OPC UA servers.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "servers": {"type": "array", "items": {"type": "string"}},
                    "skip_system_tags": {"type": "boolean", "default": True},
                },
                "required": ["servers"],
            },
            "output_schema": {"type": "string"},
            "handler": generate_prompt_batch_handler,
        },
    ],
}
