from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, ModelSettings, trace
from pydantic import BaseModel
import asyncio

load_dotenv(override=True)

NUMBER_OF_SEARCHES = 5

INSTRUCTIONS = f"""
You are a helpful research assistant. Given a query, come up with a set of web searches
to perform to best answer the query. Output {NUMBER_OF_SEARCHES} terms to query for.
"""

# Use Pydantic objects to describe the Schema of the output. 

class WebSearchItem(BaseModel):
    reason: str
    "Your reasoning for why this search is important to the query."

    query: str
    "The search term to use for the web search."

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """
    A lists of web searches to perform to best answer the query.
    """

# Pass in the Pydantic object to ensure the output follows the Schema.Agent

planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4.1-mini",
    output_type=WebSearchPlan,
)

async def main():
    with trace("Planner"):
        plan = await Runner.run(planner_agent, RESEARCH_TOPIC)

    print(plan.final_output)

if __name__ == "__main__":
    from research_config import RESEARCH_TOPIC
    asyncio.run(main())
