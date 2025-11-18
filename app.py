import gradio as gr
import asyncio
import os
from openai import RateLimitError
from agents import trace, Runner, Agent
from typing import Dict, Any

# Import from parlament_agent
from parlament_agent import (
    config,
    run_scripter_with_guardrails,
    shauli_parlament_member_tool,
    avi_parlament_member_tool,
    karkov_parlament_member_tool,
    hektor_parlament_member_tool,
    amatzia_parlament_member_tool,
    english_hebrew_translator_agent,
    gemini_model,
    scripter_agent
)


async def run_parliament_session_ui(topic: str):
    """Run the parliament session with the given topic for UI"""
    
    # Retry logic with exponential backoff for rate limit errors
    max_retries = 3
    base_delay = 30  # Start with 30 seconds for Gemini rate limits
    
    for attempt in range(max_retries):
        try:
            with trace(f"Parliament meet again - and today's topic is: {topic}"):
                prompt = config['agents']['scripter']['instructions'].format(topic)
                update_subject = prompt.format()
                result = await Runner.run(scripter_agent, update_subject)
                ("Final Script Output:\n", result.final_output)
                # Read the output files
                original_output = ""
                hebrew_output = ""
                
                try:
                    with open('output_scripts/original_script.txt', 'r', encoding='utf-8') as f:
                        original_output = f.read()
                except FileNotFoundError:
                    original_output = "Original script file not found."
                
                try:
                    with open('output_scripts/hebrew_output.txt', 'r', encoding='utf-8') as f:
                        hebrew_output = f.read()
                except FileNotFoundError:
                    hebrew_output = "Hebrew translation file not found."
                
                return original_output, hebrew_output
        
        except RateLimitError as e:
            error_msg = str(e)
            # Extract retry delay from error message if available
            import re
            retry_match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
            
            if attempt < max_retries - 1:
                if retry_match:
                    delay = float(retry_match.group(1)) + 5  # Add 5 seconds buffer
                else:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff: 30, 60, 120 seconds
                
                print(f"⚠️ Rate limit hit. Waiting {delay:.1f} seconds before retry (Attempt {attempt + 1}/{max_retries})...")
                return f"⚠️ Rate limit exceeded. The system will retry automatically in {delay:.0f} seconds. Please wait...", ""
            else:
                return f"❌ Rate limit error after {max_retries} attempts. Gemini API quota exceeded. Please try again in a few minutes.", ""
        
        except Exception as e:
            return f"❌ Error: {str(e)}", ""
    
    return "❌ Unexpected error occurred", ""

def process_topic(topic: str, progress=gr.Progress()):
    """Process the topic and return results"""
    if not topic or topic.strip() == "":
        return "⚠️ Please enter a topic", ""
    
    progress(0, desc="Validating input...")
    
    # Run the async function
    progress(0.2, desc="Starting parliament session...")
    try:
        original, hebrew = asyncio.run(run_parliament_session_ui(topic.strip()))
        progress(1.0, desc="Complete!")
        return original, hebrew
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

# Create Gradio interface
with gr.Blocks(title="Parliament Script Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🏛️ Parliament Script Generator
        
        Enter a topic for the parliament to discuss. The system will:
        1. **Validate** your input for inappropriate language
        2. **Generate** a parliament debate script
        3. **Translate** it to Hebrew
        
        ### ⚠️ Content Policy
        Topics containing toxic language or profanity will be rejected.
        """
    )
    
    with gr.Row():
        with gr.Column():
            topic_input = gr.Textbox(
                label="Discussion Topic",
                placeholder="Enter a topic for parliament discussion (e.g., 'climate change', 'education reform')",
                lines=3
            )
            
            submit_btn = gr.Button("🎭 Generate Parliament Script", variant="primary", size="lg")
            
            gr.Examples(
                examples=[
                    ["climate change"],
                    ["education reform"],
                    ["healthcare policy"],
                    ["economic development"]
                ],
                inputs=topic_input
            )
    
    gr.Markdown("---")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📜 Original Script (English)")
            original_output = gr.Textbox(
                label="Parliament Discussion",
                lines=20,
                max_lines=30,
                show_copy_button=True
            )
        
        with gr.Column():
            gr.Markdown("### 🇮🇱 Hebrew Translation")
            hebrew_output = gr.Textbox(
                label="תרגום עברי",
                lines=20,
                max_lines=30,
                show_copy_button=True,
                text_align="right"
            )
    
    submit_btn.click(
        fn=process_topic,
        inputs=[topic_input],
        outputs=[original_output, hebrew_output]
    )
    
    gr.Markdown(
        """
        ---
        💡 **Tip**: The parliament includes 5 members with different perspectives, ensuring a rich and balanced discussion.
        """
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
