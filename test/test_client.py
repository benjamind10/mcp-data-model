from opcua_client import MCPClient

client = MCPClient(["opc.tcp://localhost:4840"])
client.connect_all()

tags = client.browse_variables("opc.tcp://localhost:4840")
sim_tags = [t for t in tags if "OilAndGasPlant" in t["browse_path"]]
print(f"Found {len(sim_tags)} simulated tags")
for tag in sim_tags:
    print(tag["browse_path"], "→", tag["node_id"])

# Read one
value = client.read_value("opc.tcp://localhost:4840", sim_tags[0]["node_id"])
print("Sample value:", value)

client.disconnect_all()
