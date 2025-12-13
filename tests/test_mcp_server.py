from dotenv import load_dotenv
import asyncio
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio, MCPServerStdioParams

load_dotenv()


async def main():
    # 2. Run the Agent with a prompt
    fetch_params = MCPServerStdioParams(command="uv", args=["run", "app/the_parliement_service.py"])
    # params = {
    #     "command": "uv",
    #     "args": ["run", "app/the_parliement_service.py"],
    # }

    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_tools = await server.list_tools()

        for tool in fetch_tools:
            print(f"{tool.name}: {(tool.description or '').replace('\n', ' ')}")
    
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        agent = Agent(
            name="Account Info Agent",
            instructions="You are an agent that fetches account information using the account server tools.",
            model="gpt-4o-mini",
            mcp_servers=[server],
        )

        with trace("Running Agent to fetch account info"):
            result = await Runner.run(agent, "Call all the funtions tools, and add paramets in case needed")
            print("Runner Result:")
            print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())