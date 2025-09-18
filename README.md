# 🏭 MCP Data Model Project

A modular, simulator-driven OPC UA infrastructure built for industrial data modeling, AI agents, and future Unified Namespace integration.

---

## 📦 Project Structure

```
mcp-data-model/
│
├── simulator/                # OPC UA simulators
│   ├── __main__.py          # CLI entry point for simulators
│   ├── oil_gas_server.py   # Oil & Gas simulator
│   └── __init__.py
│
├── opcua_client/             # Multi-server OPC UA client
│   ├── client.py            # MCPClient class
│   └── __init__.py
│
├── mcp_server/              # MCP API server
│   ├── server.py            # FastAPI server with MCP protocol
│   ├── broker.py            # OPC UA tag fetching functions
│   ├── prompt_tools.py      # AI prompt generation from tags
│   ├── tool_registry.py     # MCP tool definitions
│   └── __init__.py
│
├── test/                     # Test scripts
│   └── test_client.py
│
├── main.py                   # Legacy CLI entry point
├── requirements.txt          # Python dependencies
└── README.md
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

### ✔️ OPC UA Client

Reusable Python client for:
- Connecting to multiple OPC UA servers
- Browsing full tag structures recursively
- Filtering and listing all variable tags
- Reading tag values (by `node_id`)

Located in `opcua_client/client.py`

### ✔️ MCP Server

Full-featured MCP (Model Context Protocol) server with:

- **REST API Endpoints:**
  - `GET /` - Health check
  - `GET /servers` - List known OPC UA servers
  - `GET /tags` - Get tags from a server
  - `POST /tags/batch` - Get tags from multiple servers
  - `GET /value` - Read specific tag value
  - `GET /prompt` - Generate AI prompt from server tags
  - `POST /prompt/batch` - Generate prompt from multiple servers

- **MCP Protocol Support:**
  - Compatible with MCP Inspector
  - JSON-RPC 2.0 protocol implementation
  - Tool discovery and execution

- **MCP Tools:**
  - `get_tags` - Browse tags from OPC UA server
  - `get_tags_batch` - Browse tags from multiple servers
  - `generate_prompt` - Create AI prompts from tag data
  - `generate_prompt_batch` - Create prompts from multiple servers

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or 3.12
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/benjamind10/mcp-data-model.git
cd mcp-data-model
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the System

#### Start OPC UA Simulators

```bash
# Run Oil & Gas simulator
python -m simulator --mode oil

# Run all simulators
python -m simulator --mode all
```

#### Start MCP Server

```bash
# Run MCP server on localhost:8000
python -m mcp_server.server
```

#### Test with MCP Inspector

1. Install MCP Inspector if not already installed
2. Configure Inspector to connect to: `http://localhost:8000/`
3. Use the available MCP tools to browse OPC UA data

#### Legacy CLI (main.py)

```bash
# Run simulator + client together
python main.py --mode all

# Run specific simulator
python main.py --mode sim --simulator oil

# Run client only
python main.py --mode client
```

---

## 🔧 Development Notes

- **PYTHONPATH Setup:** For local development, ensure modules can be imported:

```bash
# Windows PowerShell
$env:PYTHONPATH="."

# Linux/macOS
export PYTHONPATH=.
```

- **MCP Protocol:** The server implements MCP protocol for tool exposure to AI agents and MCP-compatible clients
- **OPC UA URLs:** Default servers run on `opc.tcp://localhost:4840`, `4841`, `4842`
- **MCP Server URL:** Runs on `http://localhost:8000` by default

---

## 🛠️ API Usage Examples

### REST API

```bash
# Health check
curl http://localhost:8000/

# Get tags from Oil & Gas server
curl "http://localhost:8000/tags?server_url=opc.tcp://localhost:4840"

# Generate AI prompt from server
curl "http://localhost:8000/prompt?server_url=opc.tcp://localhost:4840"
```

### MCP Protocol

The MCP server supports JSON-RPC calls for tool execution. Use MCP Inspector or integrate with MCP-compatible clients.

