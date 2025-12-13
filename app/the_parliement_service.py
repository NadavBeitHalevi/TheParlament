from mcp.server.fastmcp import FastMCP
from typing import Any
import logging
import app.parliament_agent_open_ai_sdk as parliament_agent_open_ai_sdk
mcp = FastMCP("account_server")

@mcp.tool(name="The_Parliament_Service", 
          description="Creates a parliamentary discussion on a given topic.")
async def get_account_info(script_topic: str) -> dict[str, Any]:
    # Simulate fetching account info (replace with real logic)
    english_script = await parliament_agent_open_ai_sdk.run_parliament_session_ui(script_topic) # type: ignore
    return {"english_script": english_script}
    

@mcp.tool(name="hello_test_tool", description="A simple tool that returns a greeting message.")
async def hello_tool() -> str:
    return "Hello, world!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("mcp.server.fastmcp").setLevel(logging.DEBUG)
    logging.info("Starting MCP server for account_server.py")
    mcp.run(transport="stdio")

    

