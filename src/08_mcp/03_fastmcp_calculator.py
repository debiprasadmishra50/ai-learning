import os
import sys

# Add src directory to Python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import FastMCP

mcp = FastMCP(name="Calculator")


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool(name="add", description="Add two numbers.", tags={"math", "arithmetic"})
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    return a / b


if __name__ == "__main__":
    print("[+] Starting calculator MCP server...")
    mcp.run(transport="stdio")  # STDIO by default, used for local development
    # mcp.run(transport="streamable-http")

##########################################################################
# Once the code is ready to be tested with a client
# npx @modelcontextprotocol/inspector <filename | http server URL>
# run it and verify the output
##########################################################################
