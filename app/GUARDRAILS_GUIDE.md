# Guardrails Configuration Guide

## Overview

The guardrails system provides multi-layer input validation and content safety for the Parliament Agent application. It protects against harmful content, injection attacks, and ensures appropriate user input.

## Architecture

### Pipeline Configuration

The guardrails use a pipeline-based architecture with the following layers:

```
Input Validation Pipeline
├── Content Safety Filter
│   ├── Profanity Detection
│   ├── Hate Speech Detection
│   ├── Harassment Detection
│   └── Blocked Pattern Matching
├── Input Injection Prevention
│   ├── SQL Injection Detection
│   ├── Code Injection Detection
│   └── Template Injection Detection
└── Input Length Validation
    ├── Maximum Length Check
    ├── Minimum Length Check
    └── Whitespace Handling
```

## Features

### 1. Content Safety Filter
Detects and handles:
- **Profanity**: Mild profanity is sanitized with asterisks
- **Hate Speech**: Detects discriminatory language patterns
- **Violent Language**: Blocks content promoting violence
- **Harmful Language**: Prevents abuse and harassment

### 2. Input Injection Prevention
Protects against:
- **SQL Injection**: Blocks SQL keywords and dangerous patterns
- **Code Injection**: Prevents script injection attempts
- **Template Injection**: Detects template expression exploits

### 3. Input Validation
Ensures:
- Input length is between 1 and 5000 characters
- Whitespace is properly stripped
- Empty inputs are rejected

## Usage

### Basic Validation (Strict Mode)

Raises an exception if input contains violations:

```python
from guardrails_config import validate_user_input

try:
    clean_input = validate_user_input(user_input)
    # Use clean_input
except ValueError as e:
    print(f"Input rejected: {e}")
```

### Safe Validation (Warnings Mode)

Returns sanitized input and warnings without raising exceptions:

```python
from guardrails_config import validate_user_input_safe

sanitized_input, warnings = validate_user_input_safe(user_input)

if warnings:
    for warning in warnings:
        print(f"⚠️  {warning}")

# Always use sanitized_input
```

### Get Guardrail Instance

Access the guardrail directly for advanced usage:

```python
from guardrails_config import get_guardrail

guardrail = get_guardrail()
results = guardrail.validate_input(user_input)

if results['is_valid']:
    print("Input is safe")
    print(f"Sanitized: {results['sanitized_input']}")
else:
    print("Violations found:")
    for violation in results['violations']:
        print(f"  - {violation}")
```

### Get Pipeline Configuration

For integration with OpenAI guardrails client:

```python
from guardrails_config import get_pipeline_config

config = get_pipeline_config()
# Use with GuardrailsAsyncOpenAI(config=config)
```

## Implementation in Parliament Agent

The guardrails are integrated into the main agent flow:

```python
async def run_parliament_session() -> str:
    raw_input_topic = input("Enter the topic for the parliament session: ")
    
    # Validate user input using enhanced guardrails
    try:
        input_topic, warnings = validate_user_input_safe(raw_input_topic)
        
        if warnings:
            print("⚠️  Input validation warnings:")
            for warning in warnings:
                print(f"   - {warning}")
        
        if input_topic != raw_input_topic:
            print(f"✏️  Input was sanitized.")
            print(f"   Original: {raw_input_topic}")
            print(f"   Sanitized: {input_topic}\n")
    
    except ValueError as e:
        print(f"❌ Input validation failed: {e}")
        return "Input validation failed."
```

## Configuration Customization

To modify guardrails, edit `guardrails_config.py`:

### Add Blocked Pattern

In `get_input_guardrail_config()`, add to the blocked_patterns:

```python
"blocked_patterns": [
    r"your_pattern_here",
    # ... existing patterns
]
```

### Adjust Confidence Threshold

```python
"confidence_threshold": 0.7  # Change to desired value
```

### Modify Length Constraints

```python
"max_length": 5000,  # Change maximum allowed length
"min_length": 1,     # Change minimum allowed length
```

## Testing

Run the demonstration test:

```bash
python test_guardrails_demo.py
```

Test cases cover:
- Clean input
- Profanity handling
- Violent language detection
- SQL injection prevention
- Code injection prevention
- Template injection prevention
- Empty input validation
- Length validation

## Security Considerations

1. **Pattern Matching**: Uses regex for flexible but performant pattern matching
2. **Sanitization**: Profanity is masked, not blocked, for better UX
3. **Logging**: All violations are logged for audit trails
4. **Singleton Pattern**: Uses single guardrail instance for consistency
5. **Thread Safety**: Consider adding locks if used in multi-threaded environments

## Integration with OpenAI Guardrails

The pipeline configuration is compatible with the `guardrails-ai` library:

```python
from guardrails_config import get_pipeline_config
from guardrails import GuardrailsAsyncOpenAI

pipeline_config = get_pipeline_config()
client = GuardrailsAsyncOpenAI(config=pipeline_config)
```

## Troubleshooting

### Input being rejected unexpectedly
- Check the violation messages in warnings
- Review the regex patterns in `get_input_guardrail_config()`
- Ensure input is properly formatted

### Profanity not being sanitized
- Verify pattern is in the `profanity_map` dictionary
- Check regex case-insensitivity flags (e.g., `(?i)`)

### Performance concerns
- Compiled patterns are cached on first load
- Consider reducing the number of patterns if needed
- Use string length validation as first check

## Best Practices

1. **Always use `validate_user_input_safe()`** for user-facing interactions
2. **Log violations** for security audits
3. **Inform users** when input is sanitized
4. **Regular updates** to blocked patterns based on new threats
5. **Test thoroughly** with edge cases
6. **Review warnings** even if input is accepted
