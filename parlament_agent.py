import os
from agents import Agent, OpenAIChatCompletionsModel, function_tool, trace, Runner
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
import toml

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
with open('config.toml', 'r') as f:
    config = toml.load(f)


gemini_client: AsyncOpenAI = AsyncOpenAI(api_key=google_api_key, base_url=GEMINI_BASE_URL)
gemini_model = OpenAIChatCompletionsModel(model='gemini-2.0-flash', 
                                          openai_client=gemini_client)

shauli_parlament_member_agent = Agent(
    name = 'Shauli',
    instructions = config['shauli']['instructions'],
    model = gemini_model
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
    handoff_description="Translate English text to Hebrew with high accuracy and natural flow."
)

scripter_agent = Agent(
    name = 'Scripter',
    instructions = config['agents']['scripter']['instructions'],
    model = "gpt-4o-mini",
    tools = [shauli_parlament_member_tool, 
             avi_parlament_member_tool, 
             karkov_parlament_member_tool, 
             hektor_parlament_member_tool, 
             amatzia_parlament_member_tool],
    handoffs=[english_hebrew_translator_agent] # This allows the copywriter to translate the script to Hebrew after writing it
    )


async def run_parliament_session() -> str:
    with trace("Parliament meet again :)"):
        # update the script with current topic
        input_topic = input("Enter the topic for the parliament session: ")
        prompt = config['agents']['scripter']['instructions'].format(input_topic)
        update_subject = prompt.format()
        result = await Runner.run(scripter_agent, update_subject)

        print(f"result: {result.final_output}...")  # Print the first 200 characters of the result


if __name__ == "__main__":
    print("Starting the parliament session...")
    asyncio.run(run_parliament_session())
    print("Parliament session ended.")
