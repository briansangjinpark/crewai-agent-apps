from dotenv import load_dotenv
from agents import Agent, Runner, WebSearchTool, ModelSettings, trace
from pydantic import BaseModel
import asyncio
from planner_agent import planner_agent
from search_agent import search_agent
from writer_agent import writer_agent
from models import WebSearchItem, WebSearchPlan, ReportData
from core.cache import cache
from utils.retry import call_agent_with_retry, planner_breaker, searcher_breaker, writer_breaker

load_dotenv(override=True)

async def plan_searches(query: str):
    """ Use the planner_agent to plan which searches to run for the query """
    cache_key = cache._generate_key("plan", query)

    async def compute():
        print("Planning searches...")
        result = await call_agent_with_retry(
            planner_agent,
            f"Query: {query}",
            planner_breaker,
            max_retries=3
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output.model_dump()

    # Check cache first, compute if not found
    cached_result = await cache.get_or_compute(cache_key, compute, ttl=3600)

    # If we got cached result, it's a dict - convert back to WebSearchPlan
    if isinstance(cached_result, dict):
        print(f"[CACHE HIT] Using cached search plan for query")
        return WebSearchPlan(**cached_result)

    return cached_result

async def perform_searches(search_plan: WebSearchPlan):
    """ Call search() for each item in the search plan """
    print("Searching...")
    tasks = [asyncio.create_task(search(item)) for item in search_plan.searches]
    results = await asyncio.gather(*tasks)
    print("Finished searching")
    return results

async def perform_searches_with_progress(search_plan: WebSearchPlan, task_id: str, task_manager):
    """Perform searches with granular progress updates"""
    results = []
    total = len(search_plan.searches)

    for idx, item in enumerate(search_plan.searches):
        # Update progress for each search
        percent = 30 + int((idx / total) * 35)  # 30-65% range for searches
        await task_manager.update_task(
            task_id,
            current_step=f"Searching: {item.query} ({idx + 1}/{total})",
            percent=percent
        )

        result = await search(item)
        results.append(result)

    return results

async def search(item: WebSearchItem):
    """ Use the search agent to run a web search for each item in the search plan """
    cache_key = cache._generate_key("search", item.query)

    # Check if cached
    cached = await cache.get(cache_key)
    if cached:
        print(f"[CACHE HIT] Using cached search result for: {item.query}")
        return cached

    # Compute and cache
    print(f"[CACHE MISS] Searching for: {item.query}")
    input = f"Search term: {item.query}\nReason for search: {item.reason}"
    result = await call_agent_with_retry(
        search_agent,
        input,
        searcher_breaker,
        max_retries=3
    )
    await cache.set(cache_key, result.final_output, ttl=7200)

    return result.final_output

async def write_report(query: str, search_results: list[str]):
    """ Use the writer_agent to write a report based on the search results """
    print("Thinking about report...")
    input = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await call_agent_with_retry(
        writer_agent,
        input,
        writer_breaker,
        max_retries=3
    )
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
