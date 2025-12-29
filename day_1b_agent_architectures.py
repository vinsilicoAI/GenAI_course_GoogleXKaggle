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
🚀 Multi-Agent Systems & Workflow Patterns

This script covers:
- Multi-agent systems with an LLM coordinator
- Sequential Workflows
- Parallel Workflows
- Loop Workflows
"""

import os
import asyncio
import sys

try:
    from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
    from google.adk.runners import InMemoryRunner
    from google.adk.tools import AgentTool, FunctionTool, google_search
    from google.genai import types
except ImportError:
    print("Error: google-adk not found. Please install it using 'pip install google-adk'")
    sys.exit(1)


async def run_multi_agent_system():
    print("\n--- Running Multi-Agent System (Research & Summarization) ---")
    
    # Research Agent
    research_agent = Agent(
        name="ResearchAgent",
        model="gemini-2.5-flash-lite",
        instruction="""You are a specialized research agent. Your only job is to use the
        google_search tool to find 2-3 pieces of relevant information on the given topic and present the findings with citations.""",
        tools=[google_search],
        output_key="research_findings",
    )

    # Summarizer Agent
    summarizer_agent = Agent(
        name="SummarizerAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Read the provided research findings: {research_findings}
        Create a concise summary as a bulleted list with 3-5 key points.""",
        output_key="final_summary",
    )

    # Root Coordinator
    root_agent = Agent(
        name="ResearchCoordinator",
        model="gemini-2.5-flash-lite",
        instruction="""You are a research coordinator. Your goal is to answer the user's query by orchestrating a workflow.
        1. First, you MUST call the `ResearchAgent` tool to find relevant information on the topic provided by the user.
        2. Next, after receiving the research findings, you MUST call the `SummarizerAgent` tool to create a concise summary.
        3. Finally, present the final summary clearly to the user as your response.""",
        tools=[
            AgentTool(research_agent),
            AgentTool(summarizer_agent)
        ],
    )

    runner = InMemoryRunner(agent=root_agent)
    print("Running query: 'What are the latest advancements in quantum computing and what do they mean for AI?'")
    response = await runner.run_debug("What are the latest advancements in quantum computing and what do they mean for AI?")
    print("\nResponse:\n", response)


async def run_sequential_workflow():
    print("\n--- Running Sequential Workflow (Blog Post Creation) ---")
    
    # Agents
    outline_agent = Agent(
        name="OutlineAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Create a blog outline for the given topic with:
        1. A catchy headline
        2. An introduction hook
        3. 3-5 main sections with 2-3 bullet points for each
        4. A concluding thought""",
        output_key="blog_outline",
    )

    writer_agent = Agent(
        name="WriterAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Following this outline strictly: {blog_outline}
        Write a brief, 200 to 300-word blog post with an engaging and informative tone.""",
        output_key="blog_draft",
    )

    editor_agent = Agent(
        name="EditorAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Edit this draft: {blog_draft}
        Your task is to polish the text by fixing any grammatical errors, improving the flow and sentence structure, and enhancing overall clarity.""",
        output_key="final_blog",
    )

    root_agent = SequentialAgent(
        name="BlogPipeline",
        sub_agents=[outline_agent, writer_agent, editor_agent],
    )

    runner = InMemoryRunner(agent=root_agent)
    print("Running query: 'Write a blog post about the benefits of multi-agent systems for software developers'")
    response = await runner.run_debug("Write a blog post about the benefits of multi-agent systems for software developers")
    print("\nResponse:\n", response)


async def run_parallel_workflow():
    print("\n--- Running Parallel Workflow (Multi-Topic Research) ---")
    
    tech_researcher = Agent(
        name="TechResearcher",
        model="gemini-2.5-flash-lite",
        instruction="Research only AI/ML trends. 3 key developments. Concise.",
        tools=[google_search],
        output_key="tech_research",
    )
    
    health_researcher = Agent(
        name="HealthResearcher",
        model="gemini-2.5-flash-lite",
        instruction="Research medical breakthroughs. 3 key advances. Concise.",
        tools=[google_search],
        output_key="health_research",
    )
    
    finance_researcher = Agent(
        name="FinanceResearcher",
        model="gemini-2.5-flash-lite",
        instruction="Research fintech trends. 3 key trends. Concise.",
        tools=[google_search],
        output_key="finance_research",
    )
    
    aggregator_agent = Agent(
        name="AggregatorAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Combine these three research findings into a single executive summary:
        Tech: {tech_research}
        Health: {health_research}
        Finance: {finance_research}
        Highlight common themes.""",
        output_key="executive_summary",
    )

    parallel_research_team = ParallelAgent(
        name="ParallelResearchTeam",
        sub_agents=[tech_researcher, health_researcher, finance_researcher],
    )

    root_agent = SequentialAgent(
        name="ResearchSystem",
        sub_agents=[parallel_research_team, aggregator_agent],
    )

    runner = InMemoryRunner(agent=root_agent)
    print("Running query: 'Run the daily executive briefing on Tech, Health, and Finance'")
    response = await runner.run_debug("Run the daily executive briefing on Tech, Health, and Finance")
    print("\nResponse:\n", response)


async def run_loop_workflow():
    print("\n--- Running Loop Workflow (Story Refinement) ---")
    
    initial_writer_agent = Agent(
        name="InitialWriterAgent",
        model="gemini-2.5-flash-lite",
        instruction="""Based on the user's prompt, write the first draft of a short story (around 100-150 words).
        Output only the story text, with no introduction or explanation.""",
        output_key="current_story",
    )

    critic_agent = Agent(
        name="CriticAgent",
        model="gemini-2.5-flash-lite",
        instruction="""You are a constructive story critic. Review the story provided below.
        Story: {current_story}

        Evaluate the story's plot, characters, and pacing.
        - If the story is well-written and complete, you MUST respond with the exact phrase: "APPROVED"
        - Otherwise, provide 2-3 specific, actionable suggestions for improvement.""",
        output_key="critique",
    )

    def exit_loop():
        """Call this function ONLY when the critique is 'APPROVED'."""
        return {"status": "approved", "message": "Story approved. Exiting refinement loop."}

    refiner_agent = Agent(
        name="RefinerAgent",
        model="gemini-2.5-flash-lite",
        instruction="""You are a story refiner. You have a story draft and critique.
        Story Draft: {current_story}
        Critique: {critique}

        Your task is to analyze the critique.
        - IF the critique is EXACTLY "APPROVED", you MUST call the `exit_loop` function and nothing else.
        - OTHERWISE, rewrite the story draft to fully incorporate the feedback from the critique.""",
        output_key="current_story",
        tools=[FunctionTool(exit_loop)],
    )

    story_refinement_loop = LoopAgent(
        name="StoryRefinementLoop",
        sub_agents=[critic_agent, refiner_agent],
        max_iterations=2,
    )

    root_agent = SequentialAgent(
        name="StoryPipeline",
        sub_agents=[initial_writer_agent, story_refinement_loop],
    )

    runner = InMemoryRunner(agent=root_agent)
    print("Running query: 'Write a short story about a lighthouse keeper who discovers a mysterious, glowing map'")
    response = await runner.run_debug("Write a short story about a lighthouse keeper who discovers a mysterious, glowing map")
    print("\nResponse:\n", response)


async def main():
    if not os.environ.get("GOOGLE_API_KEY"):
         print("⚠️  GOOGLE_API_KEY environment variable not found. Please set it.")
         # return

    # You can comment/uncomment these to run specific examples
    try:
        await run_multi_agent_system()
    except Exception as e:
        print(f"Multi-agent system failed: {e}")

    try:
        await run_sequential_workflow()
    except Exception as e:
        print(f"Sequential workflow failed: {e}")

    try:
        await run_parallel_workflow()
    except Exception as e:
        print(f"Parallel workflow failed: {e}")

    try:
        await run_loop_workflow()
    except Exception as e:
        print(f"Loop workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
