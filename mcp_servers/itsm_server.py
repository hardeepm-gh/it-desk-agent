from fastmcp import FastMCP
import sys
import sqlite3
import os

# Create MCP server
mcp = FastMCP("ITSM Server")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "tickets.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
def list_open_tickets() -> str:
    """List all open tickets. Use this to see what needs fixing."""
    conn = get_db()
    tickets = conn.execute("SELECT * FROM tickets WHERE status='open'").fetchall()
    conn.close()
    if not tickets:
        return "No open tickets."
    return "\n".join([f"{t['id']}: {t['issue_type']} - {t['description']} (User: {t['user_id']})" for t in tickets])

@mcp.tool()
def get_ticket(ticket_id: str) -> str:
    """Get details of a specific ticket by ID like T001"""
    conn = get_db()
    ticket = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    conn.close()
    if not ticket:
        return f"Ticket {ticket_id} not found."
    return f"Ticket {ticket['id']}\nUser: {ticket['user_id']}\nType: {ticket['issue_type']}\nDesc: {ticket['description']}\nStatus: {ticket['status']}\nPriority: {ticket['priority']}"

@mcp.tool()
def add_note_to_ticket(ticket_id: str, note: str) -> str:
    """Add an audit note to a ticket. Use this for logging what you did."""
    # For demo, we just log it - in real project this would write to notes table
    print(f"[AUDIT LOG]", file=sys.stderr)
    return f"Note added to {ticket_id}: {note}"

@mcp.tool()
def close_ticket(ticket_id: str, resolution: str) -> str:
    """Close a ticket with a resolution summary. This is a destructive action."""
    conn = get_db()
    conn.execute("UPDATE tickets SET status='closed' WHERE id=?", (ticket_id,))
    conn.commit()
    conn.close()
    return f"Ticket {ticket_id} closed. Resolution: {resolution}"

# Run the server
if __name__ == "__main__":
    mcp.run()