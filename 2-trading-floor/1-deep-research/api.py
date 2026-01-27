from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from main import plan_searches, perform_searches, write_report
from fastapi.middleware.cors import CORSMiddleware
from research_config import RESEARCH_TOPIC 

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    topic: str

class ResearchResponse(BaseModel):
    report: str

@app.post("/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest):
    try:
        query = request.topic
        print(f"Starting research on: {query}")
        
        # 1. Plan
        search_plan = await plan_searches(query)
        
        # 2. Search
        search_results = await perform_searches(search_plan)
        
        # 3. Write
        result = await write_report(query, search_results)
        
        return ResearchResponse(report=result.markdown_report)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}
