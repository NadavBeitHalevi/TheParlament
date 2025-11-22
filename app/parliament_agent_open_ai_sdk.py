"""Parliament Agent System - Multi-Agent Debate Generator.

Defines parliament member agents, tools, and orchestration logic for generating
parliamentary debate scripts with automatic Hebrew translation.
"""

import os
import asyncio
import re

import toml
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    function_tool,
    trace,
    Runner,
)

# Load environment variables
load_dotenv()

# Load configuration
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')

# Get the directory of this file to build correct path to config
config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
with open(config_path, 'r') as f:
    config = toml.load(f)

# Initialize AI model clients
azure_client: AsyncOpenAI = AsyncOpenAI(
    api_key=os.getenv('AZURE_API_KEY'),
    base_url=os.getenv('AZURE_ENDPOINT')
)

azure_model = OpenAIChatCompletionsModel(
    model='gpt-4o',
    openai_client=azure_client
)

gemini_client: AsyncOpenAI = AsyncOpenAI(
    api_key=google_api_key,
    base_url=GEMINI_BASE_URL
)

gemini_model = OpenAIChatCompletionsModel(
    model='gemini-2.0-flash',
    openai_client=gemini_client
)

# ============================================================================
# Parliament Member Agents
# ============================================================================

shauli_parliament_member_agent = Agent(
    name='Shauli',
    instructions=config['shauli']['instructions'],
    model=azure_model
)

amatzia_parliament_member_agent = Agent(
    name='Amatzia',
    instructions=config['amatzia']['instructions'],
    model=azure_model
)

karakov_parliament_member_agent = Agent(
    name='Karakov',
    instructions=config['karakov']['instructions'],
    model=gemini_model
)

hektor_parliament_member_agent = Agent(
    name='Hektor',
    instructions=config['hektor']['instructions'],
    model=gemini_model
)

avi_parliament_member_agent = Agent(
    name='Avi',
    instructions=config['avi']['instructions'],
    model=gemini_model
)

# Convert agents to tools for use by scripter agent
shauli_parliament_member_tool = shauli_parliament_member_agent.as_tool(
    tool_name='shauli_parliament_member',
    tool_description=config['shauli']['instructions']
)

amatzia_parliament_member_tool = amatzia_parliament_member_agent.as_tool(
    tool_name='amatzia_parliament_member',
    tool_description=config['amatzia']['instructions']
)

hektor_parliament_member_tool = hektor_parliament_member_agent.as_tool(
    tool_name='hektor_parliament_member',
    tool_description=config['hektor']['instructions']
)

avi_parliament_member_tool = avi_parliament_member_agent.as_tool(
    tool_name='avi_parliament_member',
    tool_description=config['avi']['instructions']
)

karkov_parliament_member_tool = karakov_parliament_member_agent.as_tool(
    tool_name='karkov_parliament_member',
    tool_description=config['karakov']['instructions']
)

# ============================================================================
# File I/O Tools
# ============================================================================

@function_tool
def write_hebrew_to_file(text: str) -> str:
    """Write Hebrew translation to file."""
    print("Writing Hebrew text to output.txt...")
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_scripts')
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    output_path = os.path.join(output_dir, 'hebrew_output.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
        print(f"Please review: \n\n\n{text}\n\n\n")
    return f"Hebrew text successfully written to output.txt"

@function_tool
def original_script(text: str) -> str:
    """Write original English script to file."""
    print("Writing original script...")
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_scripts')
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    
    # Clean up old output files
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith('.txt'):
                os.remove(os.path.join(output_dir, filename))
                print(f"Deleted old file: {filename}")
    
    output_path = os.path.join(output_dir, 'original_script.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
        print(f"Script saved ({len(text)} characters)")
    
    return "Original script successfully written to original_script.txt"


# ============================================================================
# Orchestration Agents
# ============================================================================

english_hebrew_translator_agent = Agent(
    name='EnglishHebrewTranslator',
    instructions=config['translator']['instructions'],
    model=gemini_model,
    tools=[original_script, write_hebrew_to_file],
    handoff_description="Translate English text and save it with high accuracy and natural flow."
)

scripter_agent = Agent(
    name='Scripter',
    instructions=config['agents']['scripter']['instructions'],
    model=gemini_model,
    tools=[
        shauli_parliament_member_tool,
        avi_parliament_member_tool,
        karkov_parliament_member_tool,
        hektor_parliament_member_tool,
        amatzia_parliament_member_tool
    ],
    handoffs=[english_hebrew_translator_agent]
)


# ============================================================================
# CLI Entry Point (unused in web interface)
# ============================================================================

async def run_parliament_session() -> str:
    """Command-line interface for running parliament session (deprecated - use web UI)."""
    raw_input_topic = input("Enter the topic for the parliament session: ")
    
    print(f"🎭 Topic: {raw_input_topic}\n")
    
    # Configuration for API rate limit retry logic
    max_retries = 3
    base_delay = 35  # Seconds to wait on rate limit
    
    for attempt in range(max_retries):
        try:
            with trace(f"Parliament Session: {raw_input_topic}"):
                # Format prompt and run scripter agent
                prompt = config['agents']['scripter']['instructions'].format(raw_input_topic)
                update_subject = prompt.format()
                result = await Runner.run(scripter_agent, update_subject)
                return f"Final Script Output:\n{result.final_output}"
        
        except RateLimitError as e:
            # Parse and handle rate limit errors
            error_msg = str(e)
            retry_match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
            
            if attempt < max_retries - 1:
                delay = float(retry_match.group(1)) + 5 if retry_match else base_delay * (2 ** attempt)
                print(f"⚠️ Rate limit. Retrying in {delay:.0f}s (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Rate limit error after {max_retries} attempts.")
                return "Rate limit exceeded. Please try again later."
        
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
    
    return "Unexpected error occurred"


if __name__ == "__main__":
    print("🏛️ Parliament Script Generator (CLI)\n")
    print("Note: Use app.py for the web interface with guardrails validation.\n")
    script_result = asyncio.run(run_parliament_session())
    print(f"\n{script_result}")
    print("\nSession ended.")
