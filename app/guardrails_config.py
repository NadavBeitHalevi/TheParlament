"""Guardrails configuration for input validation.

This module provides a wrapper around the Agents SDK GuardrailAgent to validate
user input for content safety, PII detection, and custom validation rules.
"""

import dotenv
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered, Agent
from pydantic import BaseModel

# Load environment variables for API keys
dotenv.load_dotenv()


class GuardrailsResponse(BaseModel):
    """Response model for guardrails validation.
    
    Attributes:
        success: Whether the input passed all guardrails checks
        sanitized_input: The validated/sanitized version of the input
        warnings: List of warning messages if validation failed
    """
    success: bool
    sanitized_input: str
    warnings: list[str]


class MyGuardrailsAgent:
    """Wrapper for GuardrailAgent with pre-configured validation pipeline.
    
    This agent validates user input for:
    - Content moderation (hate, violence, self-harm)
    - PII detection (SSN, phone numbers, email addresses)
    - Custom validation checks
    """

    def __init__(self):
        """Initialize the guardrails agent with validation pipeline configuration."""
        self.PIPELINE_CONFIG = { # pylint: disable=R0903 # too-few-public-methods #type: ignore
            "version": 1,
            "pre_flight": {
                "version": 1,
                "guardrails": [
                    {
                        "name": "Moderation",
                        "config": {
                            "categories": ["hate", "violence", "self-harm"],
                        },
                    },
                    {
                        "name": "Contains PII",
                        "config": {
                            "entities": ["US_SSN", "PHONE_NUMBER", "EMAIL_ADDRESS"]
                        },
                    },
                ],
            },
            "input": {
                "version": 1,
                "guardrails": [
                    {
                        "name": "Custom Prompt Check",
                        "config": {
                            "model": "gpt-4.1-mini-2025-04-14",
                            "confidence_threshold": 0.7,
                            "system_prompt_details": "Check if the text contains any math problems.",
                        },
                    },
                ],
            },
            "output": {
                "version": 1,
                "guardrails": [
                    {
                        "name": "URL Filter",
                        "config": {"url_allow_list": ["example.com"]},
                    },
                ],
            },
        }
        self.agent = Agent(
            name="UserInput Validation Agent",
            instructions="Validate and sanitize user input to ensure it adheres to content policies.",
        )

    async def validate_user_input(self, user_input: str) -> GuardrailsResponse:
        """Validate user input using the guardrails pipeline.

        Args:
            user_input: The raw user input to validate

        Returns:
            GuardrailsResponse containing validation status and sanitized input
        """
        try:
            # Run the guardrails validation pipeline (async)
            result = await Runner.run(self.agent, user_input)

            print(f"✅ Validation passed: {result.final_output}")
            return GuardrailsResponse(
                success=True,
                sanitized_input=result.final_output,
                warnings=[],
            )

        except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as exc:
            # Handle guardrail violations
            print(f"⚠️ Guardrail triggered: {exc.guardrail_result.guardrail.name}")
            return GuardrailsResponse(
                success=False,
                sanitized_input="",
                warnings=[f"Guardrail triggered: {exc.guardrail_result.guardrail.name}"],
            )
        except Exception as e:
            # Handle unexpected validation errors
            print(f"⚠️ Input validation error: {e}")
            return GuardrailsResponse(
                success=False,
                sanitized_input="",
                warnings=[f"Validation error: {str(e)}"],
            )
