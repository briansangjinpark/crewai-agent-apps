from dotenv import load_dotenv
from agents import Agent, Runner, trace
from pydantic import BaseModel
import asyncio
from models import ReportData

load_dotenv(override=True)

INSTRUCTIONS = (
    "You are a senior researcher tasked with writing a cohesive report for a research query."
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in Markdown format, and it should be lengthy and details. Aim "
    "for 5-10 pages of content, at least 1000 words."
)

writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,
)
