from opcua import Client
from opcua.ua import NodeClass
import logging

logger = logging.getLogger("OPCUAClient")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
logger.addHandler(handler)


class MCPClient:
    def __init__(self, server_urls: list[str]):
        self.server_urls = server_urls
        self.clients = {}  # url → Client

    def connect_all(self):
        for url in self.server_urls:
            try:
                logger.info(f"Connecting to {url}...")
                client = Client(url)
                client.connect()
                self.clients[url] = client
                logger.info(f"Connected to {url}")
            except Exception as e:
                logger.error(f"Failed to connect to {url}: {e}")

    def disconnect_all(self):
        for url, client in self.clients.items():
            try:
                client.disconnect()
                logger.info(f"Disconnected from {url}")
            except Exception as e:
                logger.warning(f"Failed to disconnect from {url}: {e}")

    def get_connected_servers(self):
        return list(self.clients.keys())

    def browse_variables(self, server_url: str):
        """
        Returns a flat list of variable nodes on the server, including:
            - node_id
            - browse_path
            - display_name
            - data_type
        """
        if server_url not in self.clients:
            logger.warning(f"Client not connected: {server_url}")
            return []

        client = self.clients[server_url]
        root = client.get_root_node()
        return self._browse_recursive(root, path="", filter_vars=True)

    def _browse_recursive(self, node, path="", filter_vars=False):
        """
        Recursively browse the node tree.
        If filter_vars=True, only return Variable nodes.
        """
        results = []

        try:
            children = node.get_children()
        except Exception as e:
            logger.warning(f"Failed to get children for node {node}: {e}")
            return results

        for child in children:
            try:
                display_name = child.get_display_name().Text
                node_class = child.get_node_class()
                full_path = f"{path}/{display_name}".strip("/")

                if node_class == NodeClass.Variable:
                    results.append(
                        {
                            "node_id": child.nodeid.to_string(),
                            "browse_path": full_path,
                            "display_name": display_name,
                            "data_type": str(child.get_data_type_as_variant_type()),
                        }
                    )
                elif not filter_vars:
                    results.append(
                        {
                            "node_id": child.nodeid.to_string(),
                            "browse_path": full_path,
                            "display_name": display_name,
                            "node_class": str(node_class),
                        }
                    )

                # Recurse if Object or ObjectType
                if node_class in [NodeClass.Object, NodeClass.ObjectType]:
                    results.extend(
                        self._browse_recursive(child, full_path, filter_vars)
                    )

            except Exception as e:
                logger.warning(f"Error browsing node {child}: {e}")

        return results

    def read_value(self, server_url: str, node_id: str):
        if server_url not in self.clients:
            logger.warning(f"Client not connected: {server_url}")
            return None

        client = self.clients[server_url]
        try:
            node = client.get_node(node_id)
            value = node.get_value()
            return value
        except Exception as e:
            logger.error(f"Failed to read value from {node_id}: {e}")
            return None
