import argparse
import time
from simulator import run as run_simulators
from opcua_client import MCPClient


def run_client_test():
    """Quick client test to browse a connected server."""
    servers = [
        "opc.tcp://localhost:4840",  # Oil & Gas
        "opc.tcp://localhost:4841",  # Life Sciences
        "opc.tcp://localhost:4842",  # Discrete Manufacturing
    ]

    client = MCPClient(servers)
    client.connect_all()

    for url in client.get_connected_servers():
        print(f"\n🔍 Browsing server: {url}")
        tags = client.browse_variables(url)

        if not tags:
            print("  No tags found.")
            continue

        # Filter only custom (non-server) tags if possible
        sim_tags = [
            t
            for t in tags
            if "Line" in t["browse_path"]
            or "Room" in t["browse_path"]
            or "Assembly" in t["browse_path"]
        ]
        for tag in sim_tags[:5]:
            print(f"  {tag['browse_path']} → {tag['node_id']}")

        if sim_tags:
            node_id = sim_tags[0]["node_id"]
            value = client.read_value(url, node_id)
            print(f"  Sample value from first tag: {value}")

    client.disconnect_all()


def main():
    parser = argparse.ArgumentParser(description="MCP Data Model Project CLI")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["sim", "client", "all"],
        default="sim",
        help="What to run: 'sim' for simulators, 'client' to browse/test, 'all' to do both",
    )
    parser.add_argument(
        "--simulator",
        type=str,
        choices=["oil", "life", "discrete", "all"],
        default="oil",
        help="Which simulator(s) to run (used with --mode sim or all)",
    )

    args = parser.parse_args()

    if args.mode == "sim":
        run_simulators(mode=args.simulator)

    elif args.mode == "client":
        run_client_test()

    elif args.mode == "all":
        # Always run all simulators if mode is "all"
        run_simulators(mode="all")
        time.sleep(2)  # Allow simulators to initialize
        run_client_test()

        print("\n✅ All simulators are running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested. Exiting...")


if __name__ == "__main__":
    main()
