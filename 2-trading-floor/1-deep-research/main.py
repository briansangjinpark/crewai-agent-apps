from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, ModelSettings, trace
from pydantic import BaseModel
import asyncio
from planner_agent import planner_agent, WebSearchPlan, WebSearchItem
from search_agent import search_agent
from writer_agent import writer_agent

load_dotenv(override=True)

async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    print("Planning searches...")
    result = await Runner.run(planner_agent, f"Query: {query}")
    print(f"Will perform {len(result.final_output.searches)} searches") 
    return result.final_output

async def perform_searches(search_plan: WebSearchPlan): 
    """ Call search() for each item in the search plan """
    print("Searching...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    input = f"Search term: {item.query}\nReason for search: {item.reason}"
    result = await Runner.run(search_agent, input)
    return result.final_output

async def write_report(query: str, search_results: list[str]):
    """ Use the writer_agent to write a report based on the search results """
    print("Thinking about report...")
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input)
    print("Finished writing report")
    print(f"\n--- Report ---\n{result.final_output.markdown_report}\n--------------")
    return result.final_output

from research_config import RESEARCH_TOPIC

async def main():
    # Example query to demonstrate the flow
    query = RESEARCH_TOPIC
    
    # 1. Plan
    search_plan = await plan_searches(query)
    
    # 2. Search
    search_results = await perform_searches(search_plan)
    
    # 3. Write
    await write_report(query, search_results)

if __name__ == "__main__":
    asyncio.run(main())
