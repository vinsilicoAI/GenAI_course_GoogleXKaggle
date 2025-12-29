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
🚀 Your First AI Agent: From Prompt to Action (Vinoy Version)

Welcome to the Kaggle 5-day Agents course!
This script demonstrates how to build a simple agent using the Agent Development Kit (ADK).
"""

import os
import asyncio
import sys

# Try to import ADK components.
try:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import google_search
    from google.genai import types
except ImportError:
    print("Error: google-adk not found. Please install it using 'pip install google-adk'")
    sys.exit(1)


async def main():
    # --- Setup ---
    print("--- Setup ---")
    
    # Configure API Key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("⚠️  GOOGLE_API_KEY environment variable not found.")
        print("Please set it before running this script.")
        # sys.exit(1)
    else:
        print("✅ Gemini API key found in environment.")

    # --- Section 2: Your first AI Agent with ADK ---
    
    print("\n--- Section 2: Your first AI Agent with ADK ---")
    
    # 2.2 Define your agent
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash-lite",
        description="A simple agent that can answer general questions.",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search],
    )
    print("✅ Root Agent defined.")

    # 2.3 Run your agent
    runner = InMemoryRunner(agent=root_agent)
    print("✅ Runner created.")

    # b. Run debug query
    print("\nDrafting query: 'What is Agent Development Kit from Google? ...'")
    try:
        response = await runner.run_debug("What is Agent Development Kit from Google? What languages is the SDK available in?")
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error running agent: {e}")

    # 2.5 Your Turn!
    print("\nDrafting query: 'What's the weather in London?'")
    try:
        response = await runner.run_debug("What's the weather in London?")
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error running agent: {e}")

    # --- Section 3: ADK Web Interface ---
    print("\n--- Section 3: ADK Web Interface ---")
    print("To use the ADK Web UI locally:")
    print("1. Create an agent: adk create sample-agent --model gemini-2.5-flash-lite --api_key $GOOGLE_API_KEY")
    print("2. Run the web UI: adk web --path sample-agent")


if __name__ == "__main__":
    asyncio.run(main())
