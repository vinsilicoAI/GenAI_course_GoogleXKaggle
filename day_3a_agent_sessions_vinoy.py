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
🚀 Memory Management - Part 1 - Sessions

This script demonstrates:
- Session management (InMemory & Database)
- Stateful agents
- Context Compaction
- Session State tools
"""

import os
import asyncio
import sys
import sqlite3
from typing import Any, Dict, List, Union

try:
    from google.adk.agents import Agent, LlmAgent
    from google.adk.apps.app import App, EventsCompactionConfig
    from google.adk.models.google_llm import Gemini
    from google.adk.sessions import DatabaseSessionService, InMemorySessionService
    from google.adk.runners import Runner
    from google.adk.tools.tool_context import ToolContext
    from google.genai import types
except ImportError:
    print("Error: google-adk not found. Please install it using 'pip install google-adk'")
    sys.exit(1)

# Global constants for demo
APP_NAME = "default"
USER_ID = "python_script_user"
MODEL_NAME = "gemini-2.5-flash-lite"
DB_FILE = "my_agent_data.db"
DB_URL = f"sqlite:///{DB_FILE}"


# --- Helper Dictionary Functions ---
async def run_session(
    runner_instance: Runner,
    user_queries: Union[List[str], str] = None,
    session_name: str = "default",
    session_service = None # Pass service to create session explicitly if needed
):
    print(f"\n ### Session: {session_name}")
    app_name = runner_instance.app_name

    # Create/Get session
    # Note: In a real app, you might inject the session_service differently
    # Here we rely on the runner having access to it, but runner calls mostly take session_id.
    # We need to manually create the session to ensure it exists for the runner run_async loop
    
    # We need access to the session service used by the runner. 
    # ADK Runner doesn't expose public property for session_service efficiently for this script structure
    # without passing it in or assuming global. 
    # But wait, run_async takes session_id.
    
    # Let's try to access the service from the runner if possible, or pass it.
    # The notebook code used a global `session_service`. 
    # I will pass `session_service_ref` to this function or use the global one in main context.
    
    # For this script, I'll pass the service instance as an argument where this helper is called, 
    # or handle it inside the specific demo function.
    pass 

# I will redefine run_session to be self-contained or accept the service
async def run_session_helper(runner: Runner, session_service, queries: List[str], session_id: str):
    print(f"\n ### Session: {session_id}")
    try:
        session = await session_service.create_session(
            app_name=runner.app_name, user_id=USER_ID, session_id=session_id
        )
    except Exception:
        # Session might exist
        session = await session_service.get_session(
            app_name=runner.app_name, user_id=USER_ID, session_id=session_id
        )

    for query in queries:
        print(f"\nUser > {query}")
        msg = types.Content(role="user", parts=[types.Part(text=query)])
        
        async for event in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=msg
        ):
            if event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                     print(f"Agent > {text}")


# --- Tools for Session State ---
def save_userinfo(tool_context: ToolContext, user_name: str, country: str) -> Dict[str, Any]:
    """Records user name and country in session state."""
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country
    return {"status": "success"}

def retrieve_userinfo(tool_context: ToolContext) -> Dict[str, Any]:
    """Retrieves user name and country from session state."""
    user_name = tool_context.state.get("user:name", "Username not found")
    country = tool_context.state.get("user:country", "Country not found")
    return {"status": "success", "user_name": user_name, "country": country}


# --- Demo Functions ---

async def run_in_memory_demo(retry_config):
    print("\n--- 2. InMemory Session Management ---")
    session_service = InMemorySessionService()
    root_agent = Agent(
        model=Gemini(model=MODEL_NAME, retry_options=retry_config),
        name="text_chat_bot",
        description="A text chatbot"
    )
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

    # Run conversation
    await run_session_helper(
        runner, session_service,
        ["Hi, I am Sam! What is the capital of United States?", "Hello! What is my name?"],
        "in-memory-session"
    )

    print("\n(Note: In-Memory session data is lost if script exits)")


async def run_persistent_demo(retry_config):
    print("\n--- 3. Persistent Sessions (SQLite) ---")
    session_service = DatabaseSessionService(db_url=DB_URL)
    chatbot_agent = LlmAgent(
        model=Gemini(model=MODEL_NAME, retry_options=retry_config),
        name="text_chat_bot",
        description="A text chatbot with persistent memory",
    )
    runner = Runner(agent=chatbot_agent, app_name=APP_NAME, session_service=session_service)

    # Run 1
    await run_session_helper(
        runner, session_service,
        ["Hi, I am Sam! What is the capital of the United States?", "Hello! What is my name?"],
        "db-session-01"
    )
    
    # Run 2 (Simulating resume)
    print("\n--- Resuming Session (asking again) ---")
    await run_session_helper(
        runner, session_service,
        ["What is the capital of India?", "Hello! What is my name?"],
        "db-session-01"
    )

    # Verify isolation
    print("\n--- Verifying Isolation (new session) ---")
    await run_session_helper(
        runner, session_service,
        ["Hello! What is my name?"],
        "db-session-02"
    )

    # Inspect DB
    print("\n--- Inspecting SQLite DB ---")
    if os.path.exists(DB_FILE):
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                # events table structure might vary, just checking presence
                cursor.execute("SELECT session_id, count(*) FROM events GROUP BY session_id")
                rows = cursor.fetchall()
                print("Events per session:", rows)
        except Exception as e:
            print(f"Error inspecting DB: {e}")


async def run_compaction_demo(retry_config):
    print("\n--- 4. Context Compaction ---")
    
    chatbot_agent = LlmAgent(
        model=Gemini(model=MODEL_NAME, retry_options=retry_config),
        name="text_chat_bot",
        description="A text chatbot",
    )
    
    app = App(
        name="research_app_compacting",
        root_agent=chatbot_agent,
        events_compaction_config=EventsCompactionConfig(
            compaction_interval=3,
            overlap_size=1,
        ),
    )
    
    session_service = DatabaseSessionService(db_url=DB_URL)
    runner = Runner(app=app, session_service=session_service)

    # Trigger compaction (4 turns, interval is 3)
    queries = [
        "What is the latest news about AI in healthcare?",
        "Are there any new developments in drug discovery?",
        "Tell me more about the second development you found.",
        "Who are the main companies involved in that?"
    ]
    
    await run_session_helper(runner, session_service, queries, "compaction-demo")
    
    # Verify compaction event
    print("\n--- Verifying Compaction Event ---")
    session = await session_service.get_session(
        app_name=runner.app_name, user_id=USER_ID, session_id="compaction-demo"
    )
    
    found = False
    for event in session.events:
        if event.actions and event.actions.compaction:
            print(f"✅ Found compaction event! Author: {event.author}")
            found = True
            break
    if not found:
        print("❌ No compaction event found (might need more turns or config check).")


async def run_session_state_demo(retry_config):
    print("\n--- 5. Session State Management ---")
    
    root_agent = LlmAgent(
        model=Gemini(model=MODEL_NAME, retry_options=retry_config),
        name="text_chat_bot",
        description="""A text chatbot.
        Use `save_userinfo` to record username/country.
        Use `retrieve_userinfo` to fetch them.""",
        tools=[save_userinfo, retrieve_userinfo],
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, session_service=session_service, app_name="default")

    queries = [
        "Hi, how are you? What is my name?",
        "My name is Sam. I'm from Poland.",
        "What is my name? Which country am I from?"
    ]
    
    await run_session_helper(runner, session_service, queries, "state-demo")
    
    # Inspect State
    session = await session_service.get_session(app_name="default", user_id=USER_ID, session_id="state-demo")
    print("\nSession State:", session.state)


async def main():
    if not os.environ.get("GOOGLE_API_KEY"):
         print("⚠️  GOOGLE_API_KEY environment variable not found. Please set it.")
         # return

    retry_config = types.HttpRetryOptions(
        attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429, 500, 503, 504]
    )

    # Select which demos to run
    # 1. InMemory
    try:
        await run_in_memory_demo(retry_config)
    except Exception as e:
        print(f"InMemory demo error: {e}")

    # 2. Persistent
    try:
        await run_persistent_demo(retry_config)
    except Exception as e:
        print(f"Persistent demo error: {e}")

    # 3. Compaction
    try:
        await run_compaction_demo(retry_config)
    except Exception as e:
        print(f"Compaction demo error: {e}")

    # 4. Session State
    try:
        await run_session_state_demo(retry_config)
    except Exception as e:
        print(f"Session State demo error: {e}")
        
    # Cleanup DB
    if os.path.exists(DB_FILE):
        print(f"\nCleaning up {DB_FILE}...")
        os.remove(DB_FILE)

if __name__ == "__main__":
    asyncio.run(main())
