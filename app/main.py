from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import asyncio

from guardrails_config import MyGuardrailsAgent
from guardrails.exceptions import GuardrailTripwireTriggered

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv(override=True)

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

        ga = MyGuardrailsAgent()
        ga_agent_client = ga.get_agent()

        try:
            response = await ga_agent_client.responses.create(
                model="gpt-4o-mini",
                input="Hello world! Tell me a joke.",
            )
        except GuardrailTripwireTriggered as exc:
            print(f"Guardrail triggered: {exc.guardrail_result.info}")
        # Guardrails run automatically
        print(response.llm_response.output_text)
        
        with trace("Asking on the weather"):
            result = await Runner.run(agent, "What's the weather like in Tel Aviv in the next 3 days, give me all the details you know?")
            print(result.final_output)
            

    asyncio.run(main())