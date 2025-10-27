#!/usr/bin/env python3
"""Test script for guardrails validators."""

from guardrails_config import create_parliament_guard

# Test the guard
guard = create_parliament_guard()
print('✅ Parliament guard created successfully!')
print()

# Test 1: Clean text
print('Test 1: Clean text')
try:
    result = guard.validate('This is a nice and friendly conversation.')
    print(f'✅ Passed: {result.validated_output}')
except Exception as e:
    print(f'❌ Failed: {e}')
print()

# Test 2: Profanity (should be filtered)
print('Test 2: Profanity (should be filtered)')
try:
    result = guard.validate('What the hell is going on here?')
    print(f'Result type: {type(result)}')
    print(f'Result: {result}')
    print(f'✅ Filtered output: {result.validated_output if hasattr(result, "validated_output") else "N/A"}')
except Exception as e:
    print(f'❌ Error: {e}')
print()

# Test 3: Toxic language (should be blocked)
print('Test 3: Toxic language (should be blocked)')
try:
    result = guard.validate('I hate this terrible thing.')
    print(f'❌ Should have been blocked: {result.validated_output}')
except Exception as e:
    print(f'✅ Correctly blocked: {e}')
print()

print('All tests completed!')
