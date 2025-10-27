"""
Example of how to integrate Guardrails with your Parliament agents.
"""

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner
from guardrails import Guard
from guardrails_config import create_parliament_guard, create_pii_guard

load_dotenv()


async def run_guarded_agent_example():
    """
    Example of running an agent with guardrails validation.
    """
    
    # Create the guard
    guard = create_parliament_guard()
    
    # Set up your model
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    model = OpenAIChatCompletionsModel(model='gpt-4o-mini', openai_client=client)
    
    # Create an agent
    agent = Agent(
        name='GuardedAgent',
        instructions='You are a helpful assistant that provides safe and appropriate responses.',
        model=model
    )
    
    # User input
    user_message = "Tell me about climate change."
    
    # Run the agent
    result = await Runner.run(agent, user_message)
    
    # Validate the output with guardrails
    try:
        validated_output = guard.validate(result.final_output)
        print(f"Validated Output: {validated_output.validated_output}")
        return validated_output.validated_output
    except Exception as e:
        print(f"Guardrails validation failed: {e}")
        return None


async def run_guarded_parliament_session(topic: str):
    """
    Example of running a parliament session with guardrails.
    
    Args:
        topic: The discussion topic
    """
    from parlament_agent import scripter_agent
    
    # Create guards
    content_guard = create_parliament_guard()
    pii_guard = create_pii_guard()
    
    # Run the session
    result = await Runner.run(scripter_agent, topic)
    
    # Validate with multiple guards
    try:
        # Check for content safety
        content_validated = content_guard.validate(result.final_output)
        
        # Check for PII
        pii_validated = pii_guard.validate(content_validated.validated_output)
        
        print("✅ All guardrails passed!")
        return pii_validated.validated_output
        
    except Exception as e:
        print(f"❌ Guardrails validation failed: {e}")
        return None


# Wrapper function to add guardrails to any agent
async def run_with_guardrails(agent, message: str, guards: list):
    """
    Generic function to run any agent with specified guardrails.
    
    Args:
        agent: The agent to run
        message: The input message
        guards: List of Guard objects to validate with
    
    Returns:
        Validated output or None if validation fails
    """
    result = await Runner.run(agent, message)
    
    output = result.final_output
    
    # Apply each guard sequentially
    for guard in guards:
        try:
            validated = guard.validate(output)
            output = validated.validated_output
        except Exception as e:
            print(f"Guardrail failed: {e}")
            return None
    
    return output


if __name__ == "__main__":
    import asyncio
    
    # Example 1: Simple guarded agent
    print("=== Example 1: Simple Guarded Agent ===")
    asyncio.run(run_guarded_agent_example())
    
    # Example 2: Guarded parliament session
    print("\n=== Example 2: Guarded Parliament Session ===")
    asyncio.run(run_guarded_parliament_session("Discuss renewable energy"))
