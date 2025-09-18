from opcua_client import MCPClient
from mcp_server.models import OPCUATag
from typing import List


def generate_prompt_from_tags(tags: List[OPCUATag]) -> str:
    lines = [
        "You are analyzing OPC UA tag data for an industrial system.",
        "The following tags are available:",
        "",
    ]
    for tag in tags:
        lines.append(f"- {tag.browse_path} ({tag.data_type}) [{tag.node_id}]")

    lines.append("")
    lines.append(
        "Generate a structured model (e.g., JSON schema or UNS layout) that represents these tags logically."
    )
    return "\n".join(lines)
