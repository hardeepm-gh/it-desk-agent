import asyncio
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client

load_dotenv(dotenv_path=".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file!")
print(f"✅ Key loaded: {api_key[:10]}...")

openai_client = OpenAI(api_key=api_key)

# Point to your 3 MCP servers
client = Client({
    "itsm": {"command": "python", "args": ["mcp_servers/itsm_server.py"]},
    "device": {"command": "python", "args": ["mcp_servers/device_server.py"]},
    "kb": {"command": "python", "args": ["mcp_servers/kb_server.py"]},
})

SYSTEM_PROMPT = """
You are an autonomous IT Service Desk Agent.
Your goal: Fix IT tickets WITHOUT a human agent.

Workflow you MUST follow:
1. When user gives a ticket ID, call get_ticket
2. Check device status with check_device_status using the user_id from ticket
3. Search knowledge base with search_kb using issue_type
4. Execute the fix (clear_print_queue, restart_wifi_service, etc.)
5. Add audit note with add_note_to_ticket
6. Close ticket with close_ticket

Rules:
- Always log what you do (audit)
- For sensitive actions like reset_password, mention you are logging it
- Be concise but show your steps
"""

async def run():
    async with client:
        # Get tools from MCP servers
        mcp_tools = await client.list_tools()

        # Convert to OpenAI format
        openai_tools = []
        for tool in mcp_tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        print("🤖 IT Agent Ready. Type a ticket ID like T001 or 'list tickets'. Type 'exit' to quit.")
        print("-" * 60)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            messages.append({"role": "user", "content": user_input})

            # Loop for tool calls
            while True:
                response = openai_client.chat.completions.create(
                                        model="gpt-4",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"
                )

                msg = response.choices[0].message
                messages.append(msg)

                if not msg.tool_calls:
                    print(f"\nAgent: {msg.content}")
                    break

                # Execute all tool calls
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f" 🔧 Calling tool: {tool_name}({args})")

                    result = await client.call_tool(tool_name, args)
                    # result is list of content blocks
                    result_text = result[0].text if result else "Done"
                    print(f" ✅ Result: {result_text[:150]}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text
                    })

if __name__ == "__main__":
    asyncio.run(run())