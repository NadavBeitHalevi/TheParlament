"""

Parliament Agent System - Multi-Agent Debate Generator.

Defines parliament member agents, tools, and orchestration logic for generating
parliamentary debate scripts with automatic Hebrew translation.
"""

import logging
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
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from datetime import datetime

# Load environment variables
load_dotenv()

# Load configuration
# Get the directory of this file to build correct path to config
config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
with open(config_path, 'r') as f:
    config = toml.load(f)

# Load settings from config
GEMINI_BASE_URL = config['settings']['base_url']
GEMINI_MODEL = config['settings']['model']
google_api_key = os.getenv('GOOGLE_API_KEY')

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
    model=GEMINI_MODEL,
    openai_client=gemini_client
)

# ============================================================================
# Parliament Member Agents
# ============================================================================

tal_parliament_member_agent = Agent(
    name=config['Tal']['name'],
    instructions=config['Tal']['instructions'],
    model=gemini_model
)

elad_parliament_member_agent = Agent(
    name=config['Elad']['name'],
    instructions=config['Elad']['instructions'],
    model=gemini_model
)

nadav_parliament_member_agent = Agent(
    name=config['Nadav']['name'],
    instructions=config['Nadav']['instructions'],
    model=gemini_model
)

ido_parliament_member_agent = Agent(
    name=config['Ido']['name'],
    instructions=config['Ido']['instructions'],
    model=gemini_model
)

dor_parliament_member_agent = Agent(
    name=config['Dor']['name'],
    instructions=config['Dor']['instructions'],
    model=gemini_model
)

itay_parliament_member_agent = Agent(
    name=config['Itay']['name'],
    instructions=config['Itay']['instructions'],
    model=gemini_model
)

# Convert agents to tools for use by scripter agent
tal_parliament_member_tool = tal_parliament_member_agent.as_tool(
    tool_name='tal_parliament_member',
    tool_description=config['Tal']['instructions'],
    is_enabled=True
)

elad_parliament_member_tool = elad_parliament_member_agent.as_tool(
    tool_name='elad_parliament_member',
    tool_description=config['Elad']['instructions'],
    is_enabled=True
)

nadav_parliament_member_tool = nadav_parliament_member_agent.as_tool(
    tool_name='nadav_parliament_member',
    tool_description=config['Nadav']['instructions'],
    is_enabled=True
)

ido_parliament_member_tool = ido_parliament_member_agent.as_tool(
    tool_name='ido_parliament_member',
    tool_description=config['Ido']['instructions'],
    is_enabled=True
)

dor_parliament_member_tool = dor_parliament_member_agent.as_tool(
    tool_name='dor_parliament_member',
    tool_description=config['Dor']['instructions'],
    is_enabled=True
)

itay_parliament_member_tool = itay_parliament_member_agent.as_tool(
    tool_name='itay_parliament_member',
    tool_description=config['Itay']['instructions'],
    is_enabled=True)

# ============================================================================
# File I/O Tools
# ============================================================================

@function_tool
def write_hebrew_to_file(text: str) -> str:
    """Write Hebrew translation to file."""
    logging.info("Writing Hebrew text to output.txt...")
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_scripts')
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    output_path = os.path.join(output_dir, 'hebrew_output.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
        logging.info(f"Please review: \n\n\n{text}\n\n\n")
    return f"Hebrew text successfully written to output.txt"

@function_tool
def original_script(text: str) -> str:
    """Write original English script to file."""
    logging.info("Writing original script...")
    
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_scripts')
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists
    
    # Clean up old output files
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith('.txt'):
                os.remove(os.path.join(output_dir, filename))
                logging.info(f"Deleted old file: {filename}")
    
    output_path = os.path.join(output_dir, 'original_script.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
        logging.info(f"Script saved ({len(text)} characters)")
    
    return "Original script successfully written to original_script.txt"


# ============================================================================
# Call Google GenAI API using the Nano Banana SDK to create the comic page
# ============================================================================
# Configure with your Google API Key
def create_comic_panel() -> Image.Image | None: 
    logging.info("Creating comic panel using Google GenAI Nano Banana SDK...")
    print("Creating comic panel using Google GenAI Nano Banana SDK...")
    """Create a comic panel using Google GenAI Nano Banana SDK."""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=google_api_key)  # type: ignore

    prompt = """Create a LANDSCAPE(WIDE) image with all the members together in a single panel, saying togther: Leha'im! (Cheers!)
    Panel members names: Dor, Elad, Ido, Itay, Nadav, Tal (IN THAT ORDER!According to the images provided).
    The panel members age is 43 years old. Stay true to images provided. 
    When creating the comic panel, ensure each character's appearance aligns with their respective images.
    use the images name as reference for each character appearance.!!! MUST USE THE IMAGES PROVIDED AS REFERENCE FOR CHARACTER APPEARANCE AND STYLE!!!!!
    **Setting:** A typical Tel-Aviv BAR with load of people and lively atmosphere, warm lighting, rustic background
    ALL 6 MEMBERS ARE TOGETHER IN THE SAME PANEL, CHEERING TOGETHER! MUST HAVE ALL 6 MEMBERS IN THE SAME PANEL!
    **Style:** Cartoonish, vibrant colors, exaggerated expressions, dynamic poses, speech bubbles with "Leha'im!" text.
    **Composition:** LANDSCAPE(WIDE) orientation / Composition! Balanced layout with members evenly spaced, engaging body language, and clear visibility of facial features.
    **Mood:** Joyful, celebratory, energetic atmosphere reflecting camaraderie and fun.
    **Additional Elements:** Include background details like bar counter, drinks, and other patrons to enhance the setting.
    IMAGE MUST be in LANDSCAPE(WIDE) orientation / Composition.
    """

    style_images = get_parliament_images()
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt, style_images], # type: ignore
        )
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        print(f"Error generating image: {e}")
        return None

    print("Comic panel generation response received.")
    logging.info("Comic panel generation response received.")
    for index, part in enumerate(response.parts): # type: ignore
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            # Save the generated image
            # checking if file exists, overwrite if so
            if os.path.exists(f"generated_comic_panel.png"):
                os.remove(f"generated_comic_panel.png")
            image = part.as_image()
            file_name = f"generated_comic_panel.png"
            image.save(file_name)  # type: ignore
            logging.info(f"Generated comic panel saved to {file_name}")
            return image  # type: ignore
    return None

# ============================================================================
# Orchestration Agents
# ============================================================================

english_hebrew_translator_agent = Agent(
    name='EnglishHebrewTranslator',
    instructions=config['translator']['instructions'],
    model=gemini_model,
    tools=[original_script, write_hebrew_to_file],
)

scripter_agent = Agent(
    name='Scripter',
    instructions=config['agents']['scripter']['instructions'],
    model=gemini_model,
    tools=[
        tal_parliament_member_tool,
        elad_parliament_member_tool,
        nadav_parliament_member_tool,
        ido_parliament_member_tool,
        dor_parliament_member_tool,
        itay_parliament_member_tool,
    ],

    handoffs=[english_hebrew_translator_agent]
)


def get_parliament_images() -> list[Image.Image]:
    """ Load parliament images from the images folder. 
    used for simulating parliament members.
    """
    images: list[Image.Image] = []
    # Get the images directory path relative to this file
    images_dir = os.path.join(os.path.dirname(__file__), '..', 'images')
    
    if not os.path.exists(images_dir):
        logging.warning(f"Images directory not found: {images_dir}")
        return images
    
    for filename in os.listdir(images_dir):
        if filename.endswith('.png') or filename.endswith('.png'):
            image_path = os.path.join(images_dir, filename)
            try:
                img = Image.open(image_path)
                images.append(img)
                logging.info(f"Loaded image: {filename}")
            except Exception as e:
                logging.error(f"Error loading image {filename}: {e}")
    
    logging.info(f"Loaded {len(images)} images from {images_dir}")
    return images


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
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with trace(f"Parliament Session: {raw_input_topic} + {current_time}"):
                # Format prompt and run scripter agent
                prompt = config['agents']['scripter']['instructions'].format(raw_input_topic)
                update_subject = prompt.format()
                logging.info(f"🤖 Running Scripter Agent...")
                print(f"🤖 Running Scripter Agent...")
                result = await Runner.run(scripter_agent, update_subject, max_turns=30)
                logging.info("✅ Scripter Agent completed.")
                
                # Generate comic panel after agent completes
                logging.info("==============================")
                logging.info("Creating comic panel... hold tight!")
                logging.info("This may take a few moments...")
                logging.info("==============================")
                print("==============================")
                print("Creating comic panel... hold tight!")
                print("This may take a few moments...")
                print("==============================")
                
                # Call the comic panel generation function directly
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
    print("what topic would you like the parliament to debate on?")
    topic_name = input("Enter topic (or press Enter for default): ").strip() or None
    script_result = asyncio.run(run_parliament_session(topic_name=topic_name))
    print("\nSession ended.")
