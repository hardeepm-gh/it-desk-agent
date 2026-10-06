import sqlite3
import sys
from fastmcp import FastMCP

mcp = FastMCP("Device Server")
DB_PATH = "database/tickets.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
def check_device_status(user_id: str) -> str:
    """Check device status for a user"""
    conn = get_db()
    devices = conn.execute("SELECT * FROM devices WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    
    if not devices:
        return f"No devices found for user {user_id}"
    
    result = []
    for d in devices:
        result.append(f"{d['type']} ({d['id']}): {d['status']}")
    return "\n".join(result)

@mcp.tool()
def clear_print_queue(device_id: str) -> str:
    """Clear stuck print queue"""
    conn = get_db()
    conn.execute("UPDATE devices SET status='online, queue cleared' WHERE id=?", (device_id,))
    conn.commit()
    conn.close()
    # Log to stderr so it doesn't break MCP protocol
    print(f"[ACTION] Clearing print queue for {device_id}", file=sys.stderr)
    return f"Print queue cleared for device {device_id}. Status now online."

@mcp.tool()
def restart_wifi_service(device_id: str) -> str:
    """Restart wifi service on laptop"""
    conn = get_db()
    conn.execute("UPDATE devices SET status='online, wifi restarted' WHERE id=?", (device_id,))
    conn.commit()
    conn.close()
    print(f"[ACTION] Restarting wifi for {device_id}", file=sys.stderr)
    return f"Wifi service restarted for device {device_id}. Device back online."

@mcp.tool()
def flush_dns(device_id: str) -> str:
    """Flush DNS cache"""
    print(f"[ACTION] Flushing DNS for {device_id}", file=sys.stderr)
    return f"DNS flushed for device {device_id}. Connectivity restored."

@mcp.tool()
def reset_password(user_id: str) -> str:
    """Reset password - sensitive action, must be audited"""
    print(f"[ACTION] Resetting password for {user_id} - AUDITED", file=sys.stderr)
    return f"Password reset for user {user_id}. Temporary password sent via secure channel. This action was audited."

if __name__ == "__main__":
    mcp.run()