from fastmcp import FastMCP
import os

mcp = FastMCP("KB Server")

KB_PATH = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

@mcp.tool()
def search_kb(query: str) -> str:
    """Search knowledge base for troubleshooting steps. Query like 'printer' or 'wifi' or 'password'"""
    results = []
    for file in os.listdir(KB_PATH):
        if file.endswith(".md"):
            file_path = os.path.join(KB_PATH, file)
            with open(file_path, "r") as f:
                content = f.read()
                if query.lower() in content.lower() or query.lower() in file.lower():
                    results.append(f"--- Found in {file} ---\n{content}\n")
    
    if not results:
        return f"No runbook found for '{query}'. Try 'printer', 'wifi', 'password'."
    return "\n".join(results)

@mcp.tool()
def list_all_runbooks() -> str:
    """List all available runbooks"""
    files = os.listdir(KB_PATH)
    return "Available runbooks:\n" + "\n".join(files)

if __name__ == "__main__":
    mcp.run()