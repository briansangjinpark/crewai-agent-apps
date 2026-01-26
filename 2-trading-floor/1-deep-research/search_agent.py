from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, ModelSettings, trace

import asyncio

load_dotenv(override=True)

INSTRUCTIONS = """
You are a research assistant. Given a search term, you search the web for that term and 
product a concise summary of the results. The summary must 2-3 paragraphs and less than 300 
words. Capture the main points. Write succinctly, no need to have complete sentences or good 
grammar. This will be consumed by someone synthesizing a report, so it is vital you capture 
the essence and ignore any fluff. Do not include any additional commentary other than the summary
itself.
"""

search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4.1-mini",
    model_settings=ModelSettings(tool_choice="required"),
)


