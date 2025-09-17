# 🏭 MCP Data Model Project

A modular, simulator-driven OPC UA infrastructure built for industrial data modeling, AI agents, and future Unified Namespace integration.

---

## 📦 Project Structure

```
mcp-data-model/
│
├── main.py                   # CLI entry point
│
├── simulator/                # OPC UA simulators
│   ├── oil_gas_server.py
│   ├── life_sciences_server.py
│   ├── discrete_server.py
│   └── __init__.py
│
├── opcua_client/             # Multi-server OPC UA client
│   ├── client.py
│   └── __init__.py
│
├── mcp_server/               # (Future) MCP API server
│   └── __init__.py
│
└── test/                     # Test scripts
    └── test_client.py
```

---

## ✅ What Works Today

### ✔️ OPC UA Simulators

Simulate industrial environments with nested, realistic assets:

- **Oil & Gas**
  - 5 production lines with pumps, compressors, valves, and flow sensors.
  - Port: `4840`

- **Life Sciences**
  - 5 process rooms with bioreactors, centrifuges, environment monitors, and batch controllers.
  - Port: `4841`

- **Discrete Manufacturing**
  - 5 board deck assembly lines with routers, presses, conveyors, and inspection.
  - Port: `4842`

Each simulator runs a fully compliant OPC UA server and updates values every 2 seconds.

---

### ✔️ OPC UA Client

Reusable Python client for:
- Connecting to multiple OPC UA servers
- Browsing full tag structures recursively
- Filtering and listing all variable tags
- Reading tag values (by `node_id`)

Located in `opcua_client/client.py`

---

### ✔️ CLI Interface

Run and test everything through `main.py`:

#### Run a specific simulator:
```bash
python main.py --mode sim --simulator oil
```

#### Run the OPC UA client only:
```bash
python main.py --mode client
```

#### Run all simulators + client together:
```bash
python main.py --mode all
```

> ✅ Keeps running until interrupted. Simulators launch in background threads.

---

## 🚧 Coming Soon: MCP Server

The `mcp_server/` module will serve as a unified interface layer for:

- REST/GraphQL APIs for browsing and reading tags
- AI agent integration
- Subscriptions and change tracking
- Possible MQTT / UNS / Snowflake bridges

Stay tuned.

---

## 🔧 Development Notes

- Python 3.11 or 3.12 recommended
- Install dependencies:

```bash
pip install -r requirements.txt
```

- Fix `PYTHONPATH` for local dev:

```bash
# Windows PowerShell
$env:PYTHONPATH="." ; python test/test_client.py

# Linux/macOS
PYTHONPATH=. python test/test_client.py
```

---

## ✨ Author

**Ben Duran**  
Industry 4.0 Architect | OPC UA Evangelist | Builder of Smart Data Planes  
📧 ben.duran@proton.me

---

## 🛠️ License

MIT License — use freely, build boldly.
