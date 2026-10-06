import asyncio
import sqlite3
from fastmcp import Client

client = Client({
    "itsm": {"command": "python", "args": ["mcp_servers/itsm_server.py"]},
    "device": {"command": "python", "args": ["mcp_servers/device_server.py"]},
    "kb": {"command": "python", "args": ["mcp_servers/kb_server.py"]},
})

def get_text(result):
    """Handle both old and new FastMCP result formats"""
    try:
        # New format: result.content[0].text
        if hasattr(result, 'content') and result.content:
            return result.content[0].text
        # Old format: result[0].text
        if isinstance(result, list) and len(result) > 0:
            return result[0].text
        return str(result)
    except:
        return str(result)

async def fix_ticket(ticket_id: str):
    async with client:
        tools = await client.list_tools()

        def find_tool(keyword):
            for t in tools:
                if keyword in t.name:
                    return t.name
            return keyword

        print(f"\n🤖 Autonomous Agent started for {ticket_id}\n" + "-"*50)

        conn = sqlite3.connect("database/tickets.db")
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
        conn.close()

        if not row:
            print("❌ Ticket not found. Run: python setup.py")
            return

        user_id = row["user_id"]
        issue_type = row["issue_type"]

        # 1. Get ticket
        tool_name = find_tool("get_ticket")
        print(f"🔧 Calling {tool_name}")
        ticket_res = await client.call_tool(tool_name, {"ticket_id": ticket_id})
        print(f"✅ {get_text(ticket_res)}\n")

        # 2. Check device status
        tool_name = find_tool("check_device_status")
        print(f"🔧 Calling {tool_name}({user_id})")
        status_res = await client.call_tool(tool_name, {"user_id": user_id})
        status_text = get_text(status_res)
        print(f"✅ {status_text}\n")

        # 3. Search KB
        tool_name = find_tool("search_kb")
        print(f"🔧 Calling {tool_name}({issue_type})")
        kb_res = await client.call_tool(tool_name, {"query": issue_type})
        print(f"✅ Found runbook: {get_text(kb_res)[:250]}...\n")

        # 4. Fix
        if "printer" in issue_type.lower():
            conn = sqlite3.connect("database/tickets.db")
            dev = conn.execute("SELECT id FROM devices WHERE user_id=? AND type='Printer'", (user_id,)).fetchone()
            conn.close()
            device_id = dev[0] if dev else "D002"  # first one
            tool_name = find_tool("clear_print_queue")
            print(f"🔧 Calling {tool_name}({device_id})")
            fix_res = await client.call_tool(tool_name, {"device_id": device_id})
            print(f"✅ {get_text(fix_res)}\n")

        elif "wifi" in issue_type.lower():
            conn = sqlite3.connect("database/tickets.db")
            dev = conn.execute("SELECT id FROM devices WHERE user_id=? AND type='Laptop'", (user_id,)).fetchone()
            conn.close()
            device_id = dev[0] if dev else "D001" # second one
            tool_name = find_tool("restart_wifi_service")
            print(f"🔧 Calling {tool_name}({device_id})")
            fix_res = await client.call_tool(tool_name, {"device_id": device_id})
            print(f"✅ {get_text(fix_res)}\n")

            tool_name = find_tool("flush_dns")
            print(f"🔧 Calling {tool_name}({device_id})")
            dns_res = await client.call_tool(tool_name, {"device_id": device_id})
            print(f"✅ {get_text(dns_res)}\n")

        elif "password" in issue_type.lower():
            tool_name = find_tool("reset_password")
            print(f"🔧 Calling {tool_name}({user_id}) [SENSITIVE - AUDITED]")
            fix_res = await client.call_tool(tool_name, {"user_id": user_id})
            print(f"✅ {get_text(fix_res)}\n")

        # 5. Audit and Close
        tool_name = find_tool("add_note_to_ticket")
        print(f"🔧 Calling {tool_name}")
        await client.call_tool(tool_name, {"ticket_id": ticket_id, "note": f"Auto-fixed {issue_type} via runbook."})
        print(f"✅ Audit logged\n")

        tool_name = find_tool("close_ticket")
        print(f"🔧 Calling {tool_name}")
        close_res = await client.call_tool(tool_name, {"ticket_id": ticket_id, "resolution": f"Fixed {issue_type} autonomously"})
        print(f"✅ {get_text(close_res)}\n")
        print("-"*50)
        print(f"🎉 Ticket {ticket_id} RESOLVED WITHOUT HUMAN AGENT")

async def main():
    print("🤖 IT Agent Ready (No API Key Needed)")
    print("Available tickets: T001 (printer), T002 (wifi), T003 (password)")
    while True:
        tid = input("\nEnter Ticket ID to fix (e.g. T001) or 'exit': ").strip().upper()
        if tid in ["EXIT", "QUIT"]:
            break
        if tid:
            await fix_ticket(tid)

if __name__ == "__main__":
    asyncio.run(main())