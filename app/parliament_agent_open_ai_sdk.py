"""

Parliament Agent System - Multi-Agent Debate Generator.

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

from google import genai  # type: ignore
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont  # type: ignore

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
    model='gemini-2.5-flash',
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

avner_parliament_member_agent = Agent(
    name='Avner',
    instructions=config['avner']['instructions'],
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

avner_parliament_member_tool = avner_parliament_member_agent.as_tool(
    tool_name='avner_parliament_member',
    tool_description=config['avner']['instructions']
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
        avner_parliament_member_tool,
    ],
    handoffs=[english_hebrew_translator_agent]
)

# ============================================================================
# Call Google GenAI API using the Nano Banana SDK to create the comic page
# ============================================================================
# Configure with your Google API Key
def create_comic_panel() -> None:
    """Create a comic panel using Google GenAI Nano Banana SDK."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=google_api_key)  # type: ignore

    # 1. Load the style reference image
    try:
        # Assumes 'image_example.png' is in the root project directory
        style_image_path = os.path.join(os.path.dirname(__file__), '..', 'image_example.png')
        style_image = Image.open(style_image_path)
        print(f"Successfully loaded style reference image from: {style_image_path}")
    except FileNotFoundError:
        print(f"Error: Style reference image not found at '{style_image_path}'. Please place your image there.") # type: ignore
        return

    # 2. Load the script
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_scripts')
    script_path = os.path.join(output_dir, 'original_script.txt')
    with open(script_path, 'r', encoding='utf-8') as f:
        script = f.read()
        print(f"Successfully loaded script from: {script_path}")


    # Add style enforcement - Generate WITHOUT text to avoid AI text generation issues
    prompt = f"""
    You are an expert Comic Book Director and Cinematographer. Your goal is to convert a text-based dialogue script into visual comic panels.
    Select 1 panel from the script that best captures the essence of the dialogue and characters.
    Create a comic panel based on that panel, following the visual requirements below.
    IMPORTANT: Generate the comic panels WITH text ENGLISH ONLY, speech bubbles, or dialogue.
    
    Visual Requirements:
    1. **Pacing:** Break the script into logical panels (one panel = one specific visual moment)
    2. **Composition:** Use varied shots (close-up, wide shot, over-the-shoulder, etc.)
    3. **Characters:** Show who is speaking through their body language, gestures, and facial expressions
    4. **Setting:** Coffee house on Friday afternoon, warm lighting, rustic background
    5. **Style:** Snoopy (Like Snoopy Charlie Brown, Peanuts etc.) comic style, clean lines, muted color palette
    6. **Layout:** Single comic page with multiple panels arranged in a grid
    
    Character Descriptions from the style image(left to right):
    - Karakov: Zoo worker, older, quiet, dark humor in expression
    - Avi: Unemployed, sarcastic look, ready for conflict
    - Shauli: Group leader, humorous, center of attention
    - Amatzia: Taxi driver, down-to-earth, authentic
    - Hektor: Dentist, sensible, justice-oriented
    
    Script for visual interpretation: {script}
    Select one panel from the script that best captures the essence of the dialogue and characters.
    Create a comic panel based on that panel, following the visual requirements above.
    Generate the comic panel as an image and return it.
    Bubble text will be in ENGLISH ONLY
    use the style reference image provided to match character appearances and overall art style.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, style_image],
    )
    
    for index, part in enumerate(response.parts): # type: ignore
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            file_name = f"generated_comic_panel_{index + 1}.png"
            image.save(file_name)  # type: ignore
            print(f"Generated comic panel saved to {file_name}")
    
# ============================================================================
# CLI Entry Point (unused in web interface)
# ============================================================================

async def run_parliament_session(topic_name: str | None) -> str:
    """Generate parliamentary discussion script for given topic."""
    import logging
    
    # Use provided topic or default
    raw_input_topic = topic_name if topic_name else "The impact of technology on society"
    
    logging.info(f"🎭 Topic: {raw_input_topic}")
    
    # Configuration for API rate limit retry logic
    max_retries = 3
    base_delay = 35  # Seconds to wait on rate limit
    
    for attempt in range(max_retries):
        try:
            with trace(f"Parliament Session: {raw_input_topic}"):
                # Format prompt and run scripter agent
                prompt = config['agents']['scripter']['instructions'].format(raw_input_topic)
                update_subject = prompt.format()
                logging.info(f"🤖 Running Scripter Agent...")
                result = await Runner.run(scripter_agent, update_subject, max_turns=30)
                logging.info("✅ Scripter Agent completed.")
                # trying to create comic panel
                logging.info("==============================")
                logging.info("Creating comic panel... hold tight!")
                logging.info("This may take a few moments... since the script is long..")
                logging.info("==============================")
                create_comic_panel()
                return f"Final Script Output:\n{result.final_output}"
        
        except RateLimitError as e:
            # Parse and handle rate limit errors
            error_msg = str(e)
            retry_match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
            
            if attempt < max_retries - 1:
                delay = float(retry_match.group(1)) + 5 if retry_match else base_delay * (2 ** attempt)
                logging.warning(f"⚠️ Rate limit. Retrying in {delay:.0f}s (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                logging.error(f"❌ Rate limit error after {max_retries} attempts.")
                return "Rate limit exceeded. Please try again later."
        
        except Exception as e:
            logging.error(f"❌ Error: {e}")
            raise
    
    return "Unexpected error occurred"


if __name__ == "__main__":
    print("🏛️ Parliament Script Generator (CLI)\n")
    print("Note: Use app.py for the web interface with guardrails validation.\n")
    script_result = asyncio.run(run_parliament_session(topic_name=None))
    print("\nSession ended.")
