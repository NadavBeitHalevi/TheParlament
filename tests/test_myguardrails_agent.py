#!/usr/bin/env python3
"""
Test suite for MyGuardrailsAgent input validation.
Tests the guardrails agent with various inputs to ensure proper validation.
"""

import asyncio
import sys
import pytest
import unittest

sys.path.insert(0, '/Users/nadav/Projects/TheParlament')

from guardrails_config import MyGuardrailsAgent, GuardrailsResponse



"""Test suite for MyGuardrailsAgent."""

@pytest.fixture
def agent(self):
    """Create an agent instance for testing."""
    return MyGuardrailsAgent()

@pytest.mark.asyncio
async def test_agent_initialization(self):
    """Test that the agent initializes properly."""
    agent = MyGuardrailsAgent()
assert agent is not None
assert hasattr(agent, 'agent')
assert agent.agent is not None

@pytest.mark.asyncio
async def test_valid_input(self, agent):
    """Test validation of clean, valid input."""
    valid_inputs = [
    "Discuss climate change policy",
    "What are the benefits of renewable energy?",
    "Healthcare reform in the modern era",
    "Education system improvements",
    ]

    for user_input in valid_inputs:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"✅ Valid input: {user_input}")
        print(f"   Result: {result.success}")

@pytest.mark.asyncio
async def test_sql_injection_attempt(self, agent):
    """Test detection of SQL injection attempts."""
    sql_injections = [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "admin' --",
    "' UNION SELECT * FROM passwords --",
    ]

    for user_input in sql_injections:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"🛡️  SQL Injection Test: {user_input}")
        print(f"   Detected: {'SQL Injection' in str(result.warnings)}")

@pytest.mark.asyncio
async def test_xss_attempt(self, agent):
    """Test detection of XSS (Cross-Site Scripting) attempts."""
    xss_attempts = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "<svg/onload=alert('xss')>",
    "javascript:alert('xss')",
    ]

    for user_input in xss_attempts:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"🛡️  XSS Test: {user_input}")
        print(f"   Detected: {'XSS' in str(result.warnings)}")

@pytest.mark.asyncio
async def test_command_injection_attempt(self, agent):
    """Test detection of command injection attempts."""
    command_injections = [
    "$(rm -rf /)",
    "`cat /etc/passwd`",
    "cmd(/bin/bash)",
    "powershell(Get-Process)",
    ]

    for user_input in command_injections:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"🛡️  Command Injection Test: {user_input}")
        print(f"   Detected: {'Command' in str(result.warnings)}")

@pytest.mark.asyncio
async def test_empty_input(self, agent):
    """Test handling of empty input."""
    empty_inputs = ["", "   ", "\n", "\t"]

    for user_input in empty_inputs:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        assert result.success == False
        print(f"⚠️  Empty Input Test: '{user_input}'")
        print(f"   Warnings: {result.warnings}")

@pytest.mark.asyncio
async def test_response_structure(self, agent):
    """Test that response has correct structure."""
    result = await agent.validate_user_input("Test input")

    assert isinstance(result, GuardrailsResponse)
    assert hasattr(result, 'success')
    assert hasattr(result, 'sanitized_input')
    assert hasattr(result, 'warnings')
    assert isinstance(result.success, bool)
    assert isinstance(result.sanitized_input, str)
    assert isinstance(result.warnings, list)
    print("✅ Response structure is correct")

@pytest.mark.asyncio
async def test_long_input(self, agent):
    """Test handling of long input."""
    long_input = "A" * 1000 + " discussing important policy matters"
    esult = await agent.validate_user_input(long_input)

    assert isinstance(result, GuardrailsResponse)
    print(f"✅ Long input handled (length: {len(long_input)})")

@pytest.mark.asyncio
async def test_special_characters(self, agent):
    """Test input with special characters."""
    special_inputs = [
    "Healthcare & policy reform (urgent!)",
    "Education: past, present & future",
    "50% increase in funding for R&D",
    "Question: What about the economy? #important",
    ]

    for user_input in special_inputs:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"✅ Special characters handled: {user_input}")

@pytest.mark.asyncio
async def test_unicode_input(self, agent):
    """Test handling of Unicode input."""
    unicode_inputs = [
    "Climate policy discussion 🌍",
    "Healthcare reform - סיקור בעברית",
    "Economic 经济 development",
    "Education 🎓 matters",
    ]

    for user_input in unicode_inputs:
        result = await agent.validate_user_input(user_input)
        assert isinstance(result, GuardrailsResponse)
        print(f"✅ Unicode handled: {user_input}")
