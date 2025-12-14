from mcp.server.fastmcp import FastMCP
from typing import Any
import logging

mcp = FastMCP("the_parliament_service")

@mcp.tool(name="the_parliament_service_tool", 
          description="Creates a parliamentary discussion on a given topic.")
async def generate_parliamentary_script(script_topic: str) -> Any:
    # Simulate fetching account info (replace with real logic)
    logging.info(f"Generating parliamentary script for topic: {script_topic}")
    # return f"Generating parliamentary script for topic: some topic"
    if not script_topic:
        script_topic = "The impact of technology on society"
    
    # english_script = await parliament_agent_open_ai_sdk.run_parliament_session(script_topic) # type: ignore
    return f"english_script: wheather"
    

@mcp.tool(name="hello_test_tool", 
          description="A simple tool that returns a greeting message.")
async def hello_tool() -> str:
    return "Hello, world!"

def main():
    """Entry point for the MCP server."""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("mcp.server.fastmcp").setLevel(logging.DEBUG)
    logging.info("Starting MCP server for the_parliament_service.py.")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

    

