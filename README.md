# 🤖 Autonomous IT Service Desk Agent - MCP Powered

> **Fixes IT tickets without a live human agent** using Model Context Protocol (MCP), FastMCP, and autonomous tool orchestration.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![MCP](https://img.shields.io/badge/MCP-FastMCP-green) ![SQLite](https://img.shields.io/badge/DB-SQLite-orange)

### 🎬 Demo
User: Fix T001

🤖 Autonomous Agent started for T001
🔧 itsm_get_ticket -> Ticket T001: printer queue stuck
🔧 device_check_device_status(U001) -> Printer D002: error - queue stuck
🔧 kb_search_kb(printer) -> Found runbook: Printer Troubleshooting
🔧 device_clear_print_queue(D002) -> Print queue cleared, online
🔧 itsm_close_ticket -> Ticket T001 closed

🎉 Ticket T001 RESOLVED WITHOUT HUMAN AGENT

Code

### 🏗️ Architecture

This project uses **3 MCP Servers** communicating via stdio transport:

1.  **ITSM Server (`itsm_server.py`)**
    *   `list_open_tickets`, `get_ticket`, `add_note_to_ticket`, `close_ticket`
    *   Manages ticket lifecycle in SQLite

2.  **Device Server (`device_server.py`)**
    *   `check_device_status`, `clear_print_queue`, `restart_wifi_service`, `flush_dns`, `reset_password`
    *   Executes real fixes, updates device status, audit logs sensitive actions

3.  **Knowledge Base Server (`kb_server.py`)**
    *   `search_kb`, `list_all_runbooks`
    *   Searches markdown runbooks in `knowledge_base/`

**Agent (`agent_simple.py`)** - Autonomous orchestrator that:
- Reads ticket -> Checks device -> Searches KB -> Executes fix -> Audits -> Closes ticket
- No human in the loop for L1 issues (printer, wifi, password)

### 📂 Project Structure

Show less
it-desk-agent/
├── agent_simple.py # Autonomous agent (no API key needed)
├── agent.py # LLM-powered version (requires OpenAI key)
├── setup.py # Creates SQLite DB + sample tickets
├── database/
│ └── tickets.db # tickets, devices, audit_logs
├── mcp_servers/
│ ├── itsm_server.py
│ ├── device_server.py
│ └── kb_server.py
├── knowledge_base/
│ ├── printer_troubleshooting.md
│ ├── wifi_troubleshooting.md
│ └── password_reset.md
└── .env

Code

### 🚀 Quick Start (No API Key Needed)

```bash
# 1. Install
pip install fastmcp python-dotenv openai

# 2. Setup DB
python setup.py

# 3. Run autonomous agent
python agent_simple.py

Show less
Then type:

Code
T001  # Printer - queue stuck
T002  # Wifi - offline
T003  # Password reset
🧠 With LLM (Optional)
If you have an OpenAI key with billing enabled:

Bash
echo "OPENAI_API_KEY=sk-..." > .env
python agent.py
🔒 Key Features for Interview
MCP Protocol: Real-world use of Model Context Protocol with 3 servers
Autonomous Tool Calling: Agent chains 5+ tools without human input
Audit Logging: All sensitive actions (reset_password) logged to audit_logs table
Knowledge-Grounded: Fix follows runbook from KB search, not hallucinated
Deterministic + LLM: Two modes - rule-based (reliable) and LLM-based (flexible)
Extensible: Add Slack/Jira MCP server without changing agent logic
📊 Database Schema
tickets(id, user_id, issue_type, description, status, priority)
devices(id, user_id, type, status)
audit_logs(ticket_id, action, note)
🛠️ Tech Stack
Python, FastMCP, SQLite, MCP stdio transport, OpenAI (optional)

Built by Hardeep Mohan - Demonstrates Agentic AI + MCP for IT Automation