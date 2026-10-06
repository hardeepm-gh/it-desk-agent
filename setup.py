import sqlite3
import os

# Create DB
os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/tickets.db")
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS tickets")
c.execute("DROP TABLE IF EXISTS devices")
c.execute("DROP TABLE IF EXISTS users")

c.execute("""
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    department TEXT
)
""")

c.execute("""
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    type TEXT,
    status TEXT,
    ip TEXT
)
""")

c.execute("""
CREATE TABLE tickets (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    issue_type TEXT,
    description TEXT,
    status TEXT,
    priority TEXT
)
""")

# Insert mock data
c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
    ("U001", "Alice Johnson", "alice@company.com", "Finance"),
    ("U002", "Bob Smith", "bob@company.com", "Engineering"),
])

c.executemany("INSERT INTO devices VALUES (?, ?, ?, ?, ?)", [
    ("D001", "U001", "Laptop", "online", "192.168.1.10"),
    ("D002", "U001", "Printer", "error - queue stuck", "192.168.1.15"),
    ("D003", "U002", "Laptop", "offline", "192.168.1.20"),
])

c.executemany("INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?)", [
    ("T001", "U001", "printer", "I can't print - says queue stuck", "open", "medium"),
    ("T002", "U001", "wifi", "My laptop won't connect to WiFi", "open", "high"),
    ("T003", "U002", "password", "Need to reset my password", "open", "low"),
])

conn.commit()
conn.close()
print("✅ Database created at database/tickets.db")

# Create Knowledge Base files
os.makedirs("knowledge_base", exist_ok=True)

with open("knowledge_base/printer_troubleshooting.md", "w") as f:
    f.write("""
# Printer Troubleshooting Runbook
## Issue: Queue Stuck
1. Check device status via `check_device_status`
2. If status contains 'queue stuck', run `clear_print_queue`
3. Verify status again
4. If fixed, close ticket with note
""")

with open("knowledge_base/wifi_troubleshooting.md", "w") as f:
    f.write("""
# WiFi Troubleshooting Runbook
## Issue: Can't connect to WiFi
1. Check device status via `check_device_status`
2. If offline, run `restart_wifi_service` and `flush_dns`
3. Verify connectivity
4. If still failing, escalate to L2
""")

with open("knowledge_base/password_reset.md", "w") as f:
    f.write("""
# Password Reset Runbook
## Issue: Password Reset
1. Verify user identity via email
2. Run `reset_password` tool
3. Send confirmation email and close ticket
""")

print("✅ Knowledge base files created")