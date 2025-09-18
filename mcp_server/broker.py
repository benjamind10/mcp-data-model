# mcp_server/broker.py

from opcua_client import MCPClient
from mcp_server.models import OPCUATag
from mcp_server.prompt_tools import generate_prompt_from_tags


SYSTEM_NODE_NAMES = {"Server", "Types", "Views", "EventTypes", "BaseEventType"}


def get_tags_from_server(
    server_url: str, skip_system_tags: bool = True
) -> list[OPCUATag]:
    client = MCPClient([server_url])
    client.connect_all()

    all_tags = []
    raw_tags = client.browse_variables(server_url)

    # Identify simulated roots dynamically by browsing the Objects folder
    if skip_system_tags:
        simulated_roots = []
        root = client.clients[server_url].get_root_node()
        objects_node = root.get_child(["0:Objects"])
        for child in objects_node.get_children():
            name = child.get_display_name().Text
            if name not in SYSTEM_NODE_NAMES:
                simulated_roots.append(name)

        # Filter based on those discovered root names
        for tag in raw_tags:
            if any(
                tag["browse_path"].startswith(f"Objects/{root_name}")
                for root_name in simulated_roots
            ):
                all_tags.append(
                    OPCUATag(
                        server_url=server_url,
                        node_id=tag["node_id"],
                        browse_path=tag["browse_path"],
                        display_name=tag["display_name"],
                        data_type=tag["data_type"],
                    )
                )
    else:
        for tag in raw_tags:
            all_tags.append(
                OPCUATag(
                    server_url=server_url,
                    node_id=tag["node_id"],
                    browse_path=tag["browse_path"],
                    display_name=tag["display_name"],
                    data_type=tag["data_type"],
                )
            )

    client.disconnect_all()
    return all_tags


def generate_model_prompt(server_url: str, skip_system_tags: bool = True) -> str:
    tags = get_tags_from_server(server_url, skip_system_tags=skip_system_tags)
    return generate_prompt_from_tags(tags)
