# Google x Kaggle GenAI Course (Python Scripts)

This repository contains the Python script versions of the notebooks from the [Kaggle 5-day Agents course](https://www.kaggle.com/learn/intro-to-ai-agents).

## Setup

### Prerequisites

1.  **Python 3.10+** (Recommended)
2.  **Google ADK**: This course relies on the Google Agent Development Kit.
    ```bash
    pip install google-adk
    ```
3.  **Gemini API Key**: You need a Google API key for Gemini.
    -   Get one here: [Google AI Studio](https://aistudio.google.com/app/api-keys)
    -   Set it as an environment variable:
        ```bash
        export GOOGLE_API_KEY="your_api_key_here"
        ```

## detailed Scripts

### Day 1: Agents Fundamentals

*   **`day_1a_from_prompt_to_action.py`**
    *   Basic introduction to creating an Agent and running a query using `InMemoryRunner`.
    *   Demonstrates how an agent can use the `google_search` tool.

*   **`day_1b_agent_architectures.py`**
    *   Advanced agent workflows.
    *   Demonstrates:
        *   **Multi-Agent Systems**: Using a root agent to orchestrate sub-agents.
        *   **Sequential Workflows**: Running agents in a fixed pipeline.
        *   **Parallel Workflows**: Running independent agents concurrently (e.g., multi-topic research).
        *   **Loop Workflows**: Iterative refinement (e.g., writer + critic loop).

### Day 2: Agent Tools

*   **`day_2a_agent_tools_vinoy.py`**
    *   How to create **Custom Tools** from Python functions.
    *   Example: A `Currency Converter Agent` that uses fee lookup and exchange rate tools.
    *   Demonstrates **Agent Tools**: Using one agent as a tool for another (e.g., a calculation specialist).
    *   Includes **Code Execution** (Agent writing and running Python code).

### Day 3: Memory & Sessions

*   **`day_3a_agent_sessions_vinoy.py`**
    *   **Session Management**:
        *   `InMemorySessionService`: Short-term, non-persistent.
        *   `DatabaseSessionService`: Persistent sessions (using SQLite).
    *   **Context Compaction**: Automatically summarizing conversation history to save tokens.
    *   **Session State**: Using tools (`save_userinfo`, `retrieve_userinfo`) to store and retrieve state across turns.

## Usage

Run any script directly from the terminal:

```bash
python day_1a_from_prompt_to_action.py
```

Make sure your `GOOGLE_API_KEY` is set!

## Clean Up

Some scripts (Day 3) generate a local SQLite database file (`my_agent_data.db`). The script attempts to clean it up, but if you interrupt it, you may want to delete it manually if you wish to reset the state.

---
*Original Notebooks Copyright 2025 Google LLC.*
