#!/usr/bin/env python3
# coding: utf-8

# Copyright 2025 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
🚀 Agent Tools

This script demonstrates checking custom tools (Function Tools) and Agent Tools.
Example: Currency Converter Agent.
"""

import os
import asyncio
import sys

try:
    from google.genai import types
    from google.adk.agents import LlmAgent
    from google.adk.models.google_llm import Gemini
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import AgentTool, ToolContext
    from google.adk.code_executors import BuiltInCodeExecutor
except ImportError:
    print("Error: google-adk not found. Please install it using 'pip install google-adk'")
    sys.exit(1)


# --- Helper Function: Fee Lookup ---
def get_fee_for_payment_method(method: str) -> dict:
    """Looks up the transaction fee percentage for a given payment method.

    Args:
        method: The name of the payment method.

    Returns:
        Dictionary with status and fee information.
    """
    fee_database = {
        "platinum credit card": 0.02,  # 2%
        "gold debit card": 0.035,  # 3.5%
        "bank transfer": 0.01,  # 1%
    }

    fee = fee_database.get(method.lower())
    if fee is not None:
        return {"status": "success", "fee_percentage": fee}
    else:
        return {
            "status": "error",
            "error_message": f"Payment method '{method}' not found",
        }

# --- Helper Function: Exchange Rate Lookup ---
def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    """Looks up and returns the exchange rate between two currencies.

    Args:
        base_currency: The ISO 4217 currency code.
        target_currency: The ISO 4217 currency code.

    Returns:
        Dictionary with status and rate information.
    """
    rate_database = {
        "usd": {
            "eur": 0.93,
            "jpy": 157.50,
            "inr": 83.58,
        }
    }

    base = base_currency.lower()
    target = target_currency.lower()

    rate = rate_database.get(base, {}).get(target)
    if rate is not None:
        return {"status": "success", "rate": rate}
    else:
        return {
            "status": "error",
            "error_message": f"Unsupported currency pair: {base_currency}/{target_currency}",
        }


def show_python_code_and_result(response):
    """Helper to print generated code execution results."""
    # Note: 'response' type depends on what run_debug returns.
    # We assume standard ADK response structure here.
    if not hasattr(response, '__iter__'): return

    for item in response:
        # Simplified check for demonstration
        try:
             # This logic mimics the notebook traversing the response
             if hasattr(item, 'content') and item.content.parts:
                 part = item.content.parts[0]
                 if hasattr(part, 'function_response') and part.function_response:
                     resp = part.function_response.response
                     if "result" in resp:
                         print("Generated Python Response >> ", resp["result"])
        except Exception:
            pass


async def main():
    if not os.environ.get("GOOGLE_API_KEY"):
         print("⚠️  GOOGLE_API_KEY environment variable not found. Please set it.")
         # return

    retry_config = types.HttpRetryOptions(
        attempts=5,
        exp_base=7,
        initial_delay=1,
        http_status_codes=[429, 500, 503, 504],
    )

    print("\n--- 1. Basic Currency Agent with Function Tools ---")
    
    currency_agent = LlmAgent(
        name="currency_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a smart currency conversion assistant.
        1. Use `get_fee_for_payment_method()` and `get_exchange_rate()`.
        2. Calculate final amount and explain breakdown.
        """,
        tools=[get_fee_for_payment_method, get_exchange_rate],
    )

    currency_runner = InMemoryRunner(agent=currency_agent)
    print("Query: 'Convert 500 US Dollars to Euros using my Platinum Credit Card.'")
    try:
        response = await currency_runner.run_debug(
            "I want to convert 500 US Dollars to Euros using my Platinum Credit Card. How much will I receive?"
        )
        print("Response:", response)
    except Exception as e:
        print(f"Error running currency_agent: {e}")


    print("\n--- 2. Enhanced Currency Agent with Code Execution ---")

    calculation_agent = LlmAgent(
        name="CalculationAgent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a specialized calculator that ONLY responds with Python code.
        Your task is to take a request for a calculation and translate it into a single block of Python code.
        Rules:
        1. Output ONLY Python code.
        2. Code MUST print the final result.
        """,
        code_executor=BuiltInCodeExecutor(),
    )

    enhanced_currency_agent = LlmAgent(
        name="enhanced_currency_agent",
        model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
        instruction="""You are a smart currency conversion assistant.
        1. Get Transaction Fee using `get_fee_for_payment_method`.
        2. Get Exchange Rate using `get_exchange_rate`.
        3. Use the `calculation_agent` tool to generate Python code to calculate the final amount.
        4. Explain the breakdown.
        """,
        tools=[
            get_fee_for_payment_method,
            get_exchange_rate,
            AgentTool(agent=calculation_agent),
        ],
    )

    enhanced_runner = InMemoryRunner(agent=enhanced_currency_agent)
    print("Query: 'Convert 1,250 USD to INR using a Bank Transfer. Show me the precise calculation.'")
    try:
        response = await enhanced_runner.run_debug(
            "Convert 1,250 USD to INR using a Bank Transfer. Show me the precise calculation."
        )
        print("Response:", response)
        # show_python_code_and_result(response)
    except Exception as e:
        print(f"Error running enhanced agent: {e}")


if __name__ == "__main__":
    asyncio.run(main())
