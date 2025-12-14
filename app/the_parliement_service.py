from mcp.server.fastmcp import FastMCP
from typing import Any
from google import genai
import logging

mcp = FastMCP("the_parliament_service")

@mcp.tool(name="the_parliament_service_tool", 
          description="Creates a parliamentary discussion on a given topic.")
async def generate_parliamentary_script(script_topic: str) -> dict[str, Any]:
    # Simulate fetching account info (replace with real logic)
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY")) 

    prompt = (
        "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
    )

    
    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            return {    
                "script_topic": "image created",
                "english_script": f"Simulated parliamentary script on the topic: {image}"
    }
    
    logging.info(f"Generating parliamentary script for topic: {script_topic}")
    # return f"Generating parliamentary script for topic: some topic"

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

    

