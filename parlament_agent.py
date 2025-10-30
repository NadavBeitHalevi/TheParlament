import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, RateLimitError
from agents import Agent, OpenAIChatCompletionsModel, function_tool, trace, Runner, input_guardrail, GuardrailFunctionOutput
import asyncio
import toml
from typing import Dict, Any
import time


guardrail_agent = Agent(
    name='Guardrail_script_agent',
    instructions='You are an agent that follows guardrails for safe input and output handling. ' \
    'Ensure all inputs and outputs are validated accordingly. no swearing or toxic language is allowed.',
    model="gemini-2.0-flash"
)


@input_guardrail
async def run_scripter_with_guardrails(ctx, agent, message):
    """Run the guardrail agent to validate input and output."""
    result = await Runner.run(agent, message)
    return GuardrailFunctionOutput(f"found an unsafe output: {result.final_output}")
    

# Load environment variables FIRST
load_dotenv()

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
google_api_key = os.getenv('GOOGLE_API_KEY')
with open('config.toml', 'r') as f:
    config = toml.load(f)

azure_client: AsyncOpenAI = AsyncOpenAI(api_key=os.getenv('AZURE_API_KEY'),
                                         base_url=os.getenv('AZURE_ENDPOINT'))

azure_model =  OpenAIChatCompletionsModel(model='gpt-4o',
                                          openai_client=azure_client)

gemini_client: AsyncOpenAI = AsyncOpenAI(api_key=google_api_key, base_url=GEMINI_BASE_URL)
gemini_model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', 
                                          openai_client=gemini_client)

shauli_parlament_member_agent = Agent(
    name = 'Shauli',
    instructions = config['shauli']['instructions'],
    model = azure_model
    )

amatzia_parlament_member_agent = Agent(
    name = 'Amatzia',
    instructions = config['amatzia']['instructions'],
    model = gemini_model
    )

karakov_parlament_member_agent = Agent(
    name = 'Karakov',
    instructions = config['karakov']['instructions'],
    model = gemini_model
    )

hektor_parlament_member_agent = Agent(
    name = 'Hektor',
    instructions = config['hektor']['instructions'],
    model = gemini_model
    )

avi_parlament_member_agent = Agent(
    name = 'Avi',
    instructions = config['avi']['instructions'],
    model = gemini_model
    )

shauli_parlament_member_tool = shauli_parlament_member_agent.as_tool(tool_name='shauli_parliament_member', 
                                                                     tool_description=config['shauli']['instructions'])

amatzia_parlament_member_tool = amatzia_parlament_member_agent.as_tool(tool_name='amatzia_parliament_member', 
                                                                       tool_description=config['amatzia']['instructions'])

hektor_parlament_member_tool = hektor_parlament_member_agent.as_tool(tool_name='hektor_parliament_member', 
                                                                     tool_description=config['hektor']['instructions'])

avi_parlament_member_tool = avi_parlament_member_agent.as_tool(tool_name='avi_parliament_member', 
                                                               tool_description=config['avi']['instructions'])

karkov_parlament_member_tool = karakov_parlament_member_agent.as_tool(tool_name='karkov_parliament_member', 
                                                                      tool_description=config['karakov']['instructions'])

@function_tool
def write_hebrew_to_file(text: str) -> str:
    """Write Hebrew text to output.txt file"""
    print("Writing Hebrew text to output.txt...")
    
    with open('output_scripts/hebrew_output.txt', 'w', encoding='utf-8') as f:
        f.write(text)
        print(f"Please review: \n\n\n{text}\n\n\n")
    return f"Hebrew text successfully written to output.txt"

@function_tool
def original_script(text: str) -> str:
    """Write original script to output.txt file"""
    print("Writing original script to output.txt...")
    #delete old txt files
    for filename in os.listdir('output_scripts'):
        if filename.endswith('.txt'):
            os.remove(os.path.join('output_scripts', filename))
            print(f"Deleted old file: {filename}")
    with open('output_scripts/original_script.txt', 'w', encoding='utf-8') as f:
        f.write(text)
        print(f"Please review: \n\n\n{text}\n\n\n")
    return f"Original script successfully written to original_script.txt"

# English to Hebrew translator agent

english_hebrew_translator_agent = Agent(
    name='EnglishHebrewTranslator',
    instructions=config['translator']['instructions'],
    model=gemini_model,
    tools=[original_script, write_hebrew_to_file],
    handoff_description="Translate English text and save it. Once done, use the write_hebrew_to_file tool with high accuracy and natural flow."
)

scripter_agent = Agent(
    name = 'Scripter',
    instructions = config['agents']['scripter']['instructions'],
    model = gemini_model,  # Changed from gpt-3.5-turbo-1106 to avoid rate limits
    tools = [shauli_parlament_member_tool, 
             avi_parlament_member_tool, 
             karkov_parlament_member_tool, 
             hektor_parlament_member_tool, 
             amatzia_parlament_member_tool],
    handoffs=[english_hebrew_translator_agent] # This allows the copywriter to translate the script to Hebrew after writing it
    )
#input_guardrails=[run_scripter_with_guardrails]

async def run_parliament_session() -> str:
    input_topic = input("Enter the topic for the parliament session: ")

    print(f"And today's topic is: {input_topic}, let's go!")
    
    # Retry logic with exponential backoff for rate limit errors
    max_retries = 5
    base_delay = 2  # Start with 2 seconds
    
    for attempt in range(max_retries):
        try:
            with trace(f"Parliament meet again - and today's topic is: {input_topic}"):
                # update the script with current topic
                prompt = config['agents']['scripter']['instructions'].format(input_topic)
                update_subject = prompt.format()
                result = await Runner.run(scripter_agent, update_subject)
                return ("Final Script Output:\n", result.final_output)
        
        except RateLimitError as e:
            if attempt < max_retries - 1:
                # Calculate exponential backoff: 2, 4, 8, 16, 32 seconds
                delay = base_delay * (2 ** attempt)
                print(f"⚠️  Rate limit hit. Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
            else:
                print(f"❌ Rate limit error after {max_retries} attempts. Please try again later.")
                raise
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

if __name__ == "__main__":
    print("Starting the parliament session...")
    script_result = asyncio.run(run_parliament_session())
    print(script_result)
    print("Parliament session ended.")
