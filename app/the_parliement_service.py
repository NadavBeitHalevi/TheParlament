from mcp.server.fastmcp import FastMCP
from typing import Any
from google import genai
import logging
import os
import sys
from pathlib import Path
mcp = FastMCP("the_parliament_service")

@mcp.tool(name="the_parliament_service_tool", 
          description="Creates a parliamentary discussion on a given topic.")
async def generate_parliamentary_script(script_topic: str) -> dict[str, Any]:
    # Simulate fetching account info (replace with real logic)
    # 1. Force-load the .env file from the SAME directory as this script
    #    This fixes the issue where Claude runs from a different folder.
    current_dir = Path(__file__).parent
    dotenv_path = current_dir / '.env'

    try:
        from dotenv import load_dotenv
        loaded = load_dotenv(dotenv_path=dotenv_path)
        if not loaded:
            print(f"DEBUG: Could not find .env at {dotenv_path}", file=sys.stderr)
    except ImportError:
        print("DEBUG: python-dotenv not installed. Please pip install python-dotenv", file=sys.stderr)

    # 2. NOW import your heavy libraries (like google-genai)
    try:
        from google import genai
    except ImportError:
        # This catches the specific error you are seeing
        print("CRITICAL: 'google-genai' library not found. Check your python path!", file=sys.stderr)
        sys.exit(1)
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY")) 

    prompt = (
        "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
    )
    logging.info("Generated content from Gemini model.")
    logging.info("Processing generated content parts.")
    for part in response.parts: # type : ignore
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            logging.info("Generated image part, simulating parliamentary script generation.")
            return {    
                "script_topic": "image created",
                "english_script": f"Simulated parliamentary script on the topic: {image}"
            }
    
    logging.info(f"Generating parliamentary script for topic: {script_topic}")
    return {
        "script_topic": script_topic,
        "english_script": f"Simulated parliamentary script on the topic: {script_topic}"
    }

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

    

