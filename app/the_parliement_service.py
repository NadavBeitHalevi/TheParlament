import sys
from pathlib import Path

# Add project root to Python path to import app modules
# This ensures imports work even when file is copied to temp directory
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add app directory as fallback for when running in original location
app_dir = Path(__file__).resolve().parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from mcp.server.fastmcp import FastMCP
from typing import Any
import logging

# Try importing from package first, then fallback to direct import
try:
    from app import parliament_agent_open_ai_sdk
except ImportError:
    import parliament_agent_open_ai_sdk



mcp = FastMCP("the_parliament_service")

@mcp.tool(name="The_Parliament_Service", 
          description="Creates a parliamentary discussion on a given topic.")
async def generate_parliamentary_script(script_topic: str) -> Any:
    # Simulate fetching account info (replace with real logic)
    logging.info(f"Generating parliamentary script for topic: {script_topic}")
    # return f"Generating parliamentary script for topic: some topic"
    if not script_topic:
        script_topic = "The impact of technology on society"
    
    english_script = await parliament_agent_open_ai_sdk.run_parliament_session(script_topic) # type: ignore
    return f"english_script: {english_script}"
    

@mcp.tool(name="hello_test_tool", description="A simple tool that returns a greeting message.")
async def hello_tool() -> str:
    return "Hello, world!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("mcp.server.fastmcp").setLevel(logging.DEBUG)
    logging.info("Starting MCP server for the_parliament_service.py.")
    mcp.run(transport="stdio")

    

