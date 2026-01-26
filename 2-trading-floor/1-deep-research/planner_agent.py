from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, ModelSettings, trace
from pydantic import BaseModel
import asyncio
from models import WebSearchPlan

load_dotenv(override=True)

NUMBER_OF_SEARCHES = 5

INSTRUCTIONS = f"""
You are a helpful research assistant. Given a query, come up with a set of web searches
to perform to best answer the query. Output {NUMBER_OF_SEARCHES} terms to query for.
"""

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4.1-mini",
    output_type=WebSearchPlan,
)
