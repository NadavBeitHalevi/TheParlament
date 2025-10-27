#!/usr/bin/env python3
"""Test script for content safety guard."""

from guardrails_config import create_content_safety_guard

# Test the content safety guard
guard = create_content_safety_guard()
print('✅ Content safety guard created successfully!')
print()

# Test 1: Safe topic
print('Test 1: Safe topic')
try:
    result = guard.validate('climate change')
    print(f'✅ Passed: "{result.validated_output}"')
except Exception as e:
    print(f'❌ Failed: {e}')
print()

# Test 2: Topic with profanity
print('Test 2: Topic with profanity')
try:
    result = guard.validate('what the hell is happening')
    print(f'✅ Passed: "{result.validated_output}"')
except Exception as e:
    print(f'✅ Correctly rejected: {e}')
print()

# Test 3: Topic with toxic language
print('Test 3: Topic with toxic language')
try:
    result = guard.validate('I hate this topic')
    print(f'❌ Should have been rejected: "{result.validated_output}"')
except Exception as e:
    print(f'✅ Correctly rejected: {e}')
print()

print('All content safety tests completed!')
