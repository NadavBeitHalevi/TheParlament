"""Parliament Script Generator - Gradio Web Interface.

A web application that generates parliamentary debate scripts on any topic.
Features input validation, multi-agent debate generation, and Hebrew translation.
"""

import asyncio
import logging
import os
import re
from typing import Any, Tuple

import gradio as gr
from gradio.themes import Soft
from openai import RateLimitError
from agents import trace, Runner
from guardrails_config import MyGuardrailsAgent

# Import parliament components
from parliament_agent_open_ai_sdk import config, scripter_agent

class GuardrailsValidationError(Exception):
    """Exception raised when guardrails validation fails.
    
    Used to distinguish validation errors from other runtime errors
    for proper error handling and user feedback.
    """
    pass


async def run_parliament_session_ui(topic: str) -> Tuple[str, str, Any]:
    """Run parliament session: validate input, generate debate, translate to Hebrew.
    
    Args:
        topic: The discussion topic for the parliament
        
    Returns:
        Tuple of (original_script, hebrew_translation, comic_image)
        
    Raises:
        GuardrailsValidationError: If input validation fails
    """
    # Configuration for API rate limit retry logic
    max_retries = 3
    base_delay = 30  # Gemini API rate limit delay in seconds

    # Step 1: Validate input using guardrails
    try:
        print("Validating input with guardrails...")
        agent = MyGuardrailsAgent()       
        
        validation_result = await agent.validate_user_input(topic)
        
        if not validation_result.success:
            error_msg = ", ".join(validation_result.warnings)
            raise GuardrailsValidationError(error_msg)
        
        # Use the sanitized/validated input
        validation_result = validation_result.sanitized_input
        print(f"✅ Input validated: {validation_result}")
    
    except GuardrailsValidationError:
        raise  # Re-raise for proper error handling in process_topic
    except Exception as e:
        print(f"❌ Validation error: {e}")
        raise GuardrailsValidationError(f"Validation error: {str(e)}")
    
    # Step 2: Generate parliament debate with retry logic
    for attempt in range(max_retries):
        try:
            with trace(f"Parliament Session: {topic}"):
                # Format the prompt and run the scripter agent
                prompt = config['agents']['scripter']['instructions'].format(topic + validation_result)
                update_subject = prompt.format()
                result = await Runner.run(scripter_agent, update_subject, max_turns=30)
                logging.info("✅ Parliament session completed.")
                logging.info(f"Parliament session result: {result}")
                # Read generated output files
                original_output = ""
                hebrew_output = ""
                comic_image = None
                
                try:
                    output_path = os.path.join(os.path.dirname(__file__), '..', 'output_scripts', 'original_script.txt')
                    with open(output_path, 'r', encoding='utf-8') as f:
                        original_output = f.read()
                        # now, lets try to generate an image based on the script
                except FileNotFoundError:
                    original_output = "Original script file not found."
                except Exception as e:
                    original_output = f"Error reading original script: {str(e)}"
                
                try:
                    output_path = os.path.join(os.path.dirname(__file__), '..', 'output_scripts', 'hebrew_output.txt')
                    # Check file exists and is recent
                    if os.path.exists(output_path):
                        with open(output_path, 'r', encoding='utf-8') as f:
                            hebrew_output = f.read()
                        logging.info(f"✅ Hebrew translation loaded: {len(hebrew_output)} characters")
                    else:
                        hebrew_output = "Hebrew translation file not found."
                except FileNotFoundError:
                    hebrew_output = "Hebrew translation file not found."
                except Exception as e:
                    logging.error(f"Error reading Hebrew translation: {str(e)}")
                    hebrew_output = f"Error reading Hebrew translation: {str(e)}"
                
                # Load the generated comic panel - refresh from disk each time
                comic_image = None
                try:
                    parliament_image = os.path.join(os.path.dirname(__file__), '..', 'generated_comic_panel.png')
                    if os.path.exists(parliament_image):
                        from PIL import Image
                        # Force reload from disk by creating new Image object
                        img = Image.open(parliament_image)
                        img.load()  # Ensure image data is loaded
                        comic_image = img.copy()  # Create a copy to avoid caching issues
                        logging.info(f"✅ Comic panel loaded successfully: {parliament_image} (size: {img.size})")
                    else:
                        logging.warning(f"⚠️ Comic panel not found at: {parliament_image}")
                except Exception as e:
                    logging.error(f"Error loading generated comic panel: {str(e)}")

                return original_output, hebrew_output, comic_image
        
        except RateLimitError as e:
            # Parse retry delay from API error message
            error_msg = str(e)
            retry_match = re.search(r'retry in (\d+\.?\d*)s', error_msg)
            
            if attempt < max_retries - 1:
                # Calculate delay: use API suggestion or exponential backoff
                if retry_match:
                    delay = float(retry_match.group(1)) + 5
                else:
                    delay = base_delay * (2 ** attempt)  # 30s, 60s, 120s
                
                print(f"⚠️ Rate limit. Retry {attempt + 1}/{max_retries} in {delay:.1f}s")
                return f"⚠️ Rate limit exceeded. Retrying in {delay:.0f} seconds...", "", None
            else:
                return f"❌ Rate limit error after {max_retries} attempts. Try again in a few minutes.", "", None
        
        except Exception as e:
            return f"❌ Error: {str(e)}", "", None
    
    return "❌ Unexpected error occurred", "", None

def process_topic(topic: str, progress: gr.Progress = gr.Progress()) -> Tuple[str, str, Any, str]:
    """Process user topic through validation and parliament generation pipeline.
    
    Args:
        topic: The discussion topic entered by the user
        progress: Gradio progress indicator
        
    Returns:
        Tuple of (original_output, hebrew_output, comic_image, error_message)
        error_message is empty string on success
    """
    if not topic or topic.strip() == "":
        return "", "", None, "⚠️ Please enter a topic"
    
    progress(0, desc="Validating input...")
    progress(0.2, desc="Starting parliament session...")
    try:
        original, hebrew, comic_img = asyncio.run(run_parliament_session_ui(topic.strip()))
        progress(1.0, desc="Complete!")
        return original, hebrew, comic_img, ""
    except GuardrailsValidationError as e:
        return "", "", None, f"🛡️ Input Validation Failed\n\n{str(e)}"
    except Exception as e:
        return "", "", None, f"❌ Error: {str(e)}"

# ============================================================================
# Gradio Web Interface
# ============================================================================
with gr.Blocks(title="Parliament Script Generator", theme=Soft()) as demo:
    # Error display components
    error_output = gr.Textbox(visible=False)
    
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
            
            gr.Examples( # type: ignore
                examples=[
                    ["Real estate market in Israel"],
                    ["climate change"],
                    ["education reform"],
                    ["healthcare policy"],
                    ["economic development"]
                ],
                inputs=[topic_input],
                outputs=None
            )
    
    # Error display area
    with gr.Row():
        error_alert = gr.HTML(value="", visible=False)
    
    gr.Markdown("---")
    
    with gr.Row(max_height=600):
        # create image placeholder
        comic_image = gr.Image(label="🎨 Generated Comic Panel", 
                               type="pil",
                               visible=False,
                               height=600,

                               )
    gr.Markdown("---")
    gr.Markdown("---")

    with gr.Row():
        with gr.Column():
            gr.Markdown("### 📜 Original Script (English)")
            original_output = gr.Textbox(
                label="Parliament Discussion",
                lines=20,
                max_lines=30
            )
        
        with gr.Column():
            gr.Markdown("### 🇮🇱 Hebrew Translation")
            hebrew_output = gr.Textbox(
                label="תרגום עברי",
                lines=20,
                max_lines=30,
                rtl=True
            )
    

    
    def handle_submit(topic: str):
        """Handle form submission and display results or errors."""
        original, hebrew, comic_img, error = process_topic(topic)
        
        if error:
            # Show error in alert box
            error_html = f"""
            <div style="background-color: #fee; border: 2px solid #f00; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                <div style="color: #c00; font-weight: bold; margin-bottom: 10px; font-size: 16px;">⚠️ Validation Error</div>
                <div style="color: #333; font-family: monospace; white-space: pre-wrap; word-wrap: break-word;">{error}</div>
            </div>
            """
            return (gr.update(value=original), 
                    gr.update(value=hebrew), 
                    gr.update(value=None, visible=False), 
                    gr.update(value="", visible=False), 
                    gr.update(value=error_html, visible=True))
        
        # Clear error and show results with comic image
        comic_visible = comic_img is not None
        return (gr.update(value=original), 
                gr.update(value=hebrew), 
                gr.update(value=comic_img, visible=comic_visible), 
                gr.update(value="", visible=False), 
                gr.update(value="", visible=False))
    
    submit_btn.click(
        fn=handle_submit,
        inputs=[topic_input],
        outputs=[original_output, hebrew_output, comic_image, error_output, error_alert]
    )
    
    gr.Markdown(
        """
        ---
        💡 **Tip**: The parliament includes 5 members with different perspectives, ensuring a rich and balanced discussion.
        """
    )

if __name__ == "__main__":
    demo.launch(share=True, 
                server_name="0.0.0.0", 
                server_port=7860)
