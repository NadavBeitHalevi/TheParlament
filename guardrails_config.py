"""
Guardrails configuration for TheParlament project.
This module defines guardrails to ensure safe and appropriate AI agent responses.
"""

from guardrails import Guard, Validator, register_validator
from guardrails.classes.validation.validation_result import ValidationResult, FailResult, PassResult
from typing import Dict, Any


@register_validator(name="toxic_language", data_type="string")
class ToxicLanguageValidator(Validator):
    """
    Custom validator to detect toxic language.
    Checks for common offensive and toxic terms.
    """
    
    def __init__(self, on_fail="exception"):
        super().__init__(on_fail=on_fail)
        # Add toxic terms you want to filter
        self.toxic_terms = [
            "hate", "kill", "attack", "destroy", "violence",
            # Add more terms as needed
        ]
    
    def validate(self, value: str, metadata: Dict[str, Any] = {}) -> ValidationResult:
        """Check if the text contains toxic language."""
        if not isinstance(value, str):
            return FailResult(error_message="Input must be a string")
        
        value_lower = value.lower()
        found_toxic = [term for term in self.toxic_terms if term in value_lower]
        
        if found_toxic:
            return FailResult(
                error_message=f"Toxic language detected: {', '.join(found_toxic)}",
                fix_value=value
            )
        
        return PassResult()


@register_validator(name="profanity_free", data_type="string")
class ProfanityFreeValidator(Validator):
    """
    Custom validator to detect profanity.
    Filters out common profane words.
    """
    
    def __init__(self, on_fail="filter"):
        super().__init__(on_fail=on_fail)
        # Add profane words you want to filter
        self.profane_words = [
            "damn", "hell", "crap", "shit", "fuck",
            # Add more words as needed
        ]
    
    def validate(self, value: str, metadata: Dict[str, Any] = {}) -> ValidationResult:
        """Check if the text contains profanity."""
        if not isinstance(value, str):
            return FailResult(error_message="Input must be a string")
        
        value_lower = value.lower()
        found_profanity = [word for word in self.profane_words if word in value_lower]
        
        if found_profanity:
            # Filter mode: replace profanity with asterisks
            filtered_value = value
            for word in found_profanity:
                filtered_value = filtered_value.replace(word, '*' * len(word))
                filtered_value = filtered_value.replace(word.capitalize(), '*' * len(word))
                filtered_value = filtered_value.replace(word.upper(), '*' * len(word))
            
            return FailResult(
                error_message=f"Profanity detected and filtered: {', '.join(found_profanity)}",
                fix_value=filtered_value
            )
        
        return PassResult()


def create_parliament_guard():
    """
    Create a guard for the parliament discussion agents that validates:
    - Toxic language (raises exception if detected)
    - Profanity (filters out profane words)
    """
    guard = Guard().use_many(
        ToxicLanguageValidator(on_fail="exception"),
        ProfanityFreeValidator(on_fail="filter")
    )
    return guard


def create_content_safety_guard():
    """
    Create a guard for content safety validation.
    This guard checks input prompts/topics for toxic language and profanity
    to ensure safe content before processing.
    
    Returns:
        Guard: A guardrails Guard instance with toxic language and profanity validators
    """
    guard = Guard().use_many(
        ToxicLanguageValidator(on_fail="exception"),
        ProfanityFreeValidator(on_fail="exception")  # Stricter - reject rather than filter
    )
    return guard


def create_pii_guard():
    """
    Create a guard to detect and prevent PII (Personally Identifiable Information) leakage.
    
    Note: To enable PII detection, install the validator:
    - guardrails hub install hub://guardrails/detect_pii
    """
    guard = Guard()
    return guard


# Guardrails configuration for different agent types
GUARDRAIL_CONFIGS = {
    "parliament_member": {
        "validators": [],
        "settings": {
            "min_length": 20,
            "max_length": 2000,
        }
    },
    "translator": {
        "validators": [],
        "settings": {
            "min_length": 10,
            "max_length": 10000,
        }
    },
    "scripter": {
        "validators": [],
        "settings": {
            "min_length": 100,
            "max_length": 5000,
        }
    }
}
