from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Create a FastAPI app
app = FastAPI(title="Calculator MCP Server", version="0.1.0")


@app.post("/multiply")
async def multiply_numbers(a: float, b: float):
    """Multiply two numbers."""
    return {"result": a * b}


@app.post("/add")
async def add_numbers(a: float, b: float):
    """Add two numbers."""
    return {"result": a + b}


@app.post("/subtract")
async def subtract_numbers(a: float, b: float):
    """Subtract two numbers."""
    return {"result": a - b}


@app.post("/divide")
async def divide_numbers(a: float, b: float):
    """Divide two numbers."""
    return {"result": a / b}


@app.get("/health")
async def health_check():
    return {"status": "online"}


# Converting it to MCP
mcp = FastApiMCP(app, name="Calculator MCP Server")
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn

    print("[+] Starting calculator MCP server...")
    print("[+] MCP server started on http://localhost:8080")
    print("[+] Press Ctrl+C to stop server")
    print("[+] Visit http://localhost:8080/docs for API documentation")

    # uvicorn.run(app, host="0.0.0.0", port=8080)
    uvicorn.run(app, host="localhost", port=8080)
