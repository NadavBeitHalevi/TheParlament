from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import asyncio



if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # Define the agent with a function tool
    @function_tool
    def get_weather(city: str) -> str:
        return f"The weather in {city} is sunny."

    agent = Agent(
        name="WeatherAgent",
        instructions="An agent that provides weather information.",
        model="gpt-4o-mini",
        tools=[get_weather],
    )
    
    # Define the main function to run the agent
    async def main():
        with trace("Asking on the weather"):
            result = await Runner.run(agent, "What's the weather like in Tel Aviv in the next 3 days, give me all the details you know?")
            print(result.final_output)
            

    asyncio.run(main())