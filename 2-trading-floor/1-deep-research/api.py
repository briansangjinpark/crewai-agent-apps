from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uuid
import json

from core.task_manager import task_manager
from core.cache import cache
from api.middleware.rate_limit import rate_limiter

app = FastAPI()

# Add CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to research endpoints"""
    if request.url.path.startswith("/research") and request.method == "POST":
        client_id = request.client.host if request.client else "unknown"
        allowed, info = rate_limiter.check_rate_limit(client_id)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {info['retry_after']}s. "
                       f"Limit: {info['limit']} requests per minute.",
                headers={
                    "X-RateLimit-Limit": str(info['limit']),
                    "X-RateLimit-Remaining": str(info['remaining']),
                    "Retry-After": str(info['retry_after'])
                }
            )

    response = await call_next(request)
    return response


class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    task_id: str
    status: str
    stream_url: str


@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start a new research task and return task ID for tracking"""
    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id)

    # Run research in background
    background_tasks.add_task(run_research_task, task_id, request.topic)

    return ResearchResponse(
        task_id=task_id,
        status="processing",
        stream_url=f"/research/{task_id}/stream"
    )


@app.get("/research/{task_id}/stream")
async def stream_progress(task_id: str):
    """Stream real-time progress updates via Server-Sent Events"""

    async def event_generator():
        queue = await task_manager.subscribe(task_id)

        # Send current state immediately
        if current_task := task_manager.get_task(task_id):
            yield {
                "event": "progress",
                "data": json.dumps({
                    "status": current_task.status,
                    "current_step": current_task.current_step,
                    "percent": current_task.percent,
                    "result": current_task.result,
                    "error": current_task.error
                })
            }

        # Stream updates as they come
        while True:
            try:
                task = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {
                    "event": "progress",
                    "data": json.dumps({
                        "status": task.status,
                        "current_step": task.current_step,
                        "percent": task.percent,
                        "result": task.result,
                        "error": task.error
                    })
                }

                # Close connection after completion or failure
                if task.status in ["completed", "failed"]:
                    break
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield {"event": "ping", "data": "keepalive"}

    return EventSourceResponse(event_generator())


@app.get("/research/{task_id}")
async def get_task_status(task_id: str):
    """Get current task status (polling fallback)"""
    if task := task_manager.get_task(task_id):
        return {
            "task_id": task_id,
            "status": task.status,
            "current_step": task.current_step,
            "percent": task.percent,
            "result": task.result,
            "error": task.error
        }
    raise HTTPException(status_code=404, detail="Task not found")


async def run_research_task(task_id: str, topic: str):
    """Background task that runs the research workflow with progress updates"""
    try:
        from main import plan_searches, perform_searches_with_progress, write_report

        # Step 1: Planning
        await task_manager.update_task(
            task_id,
            status="planning",
            current_step="Planning research strategy...",
            percent=10
        )
        search_plan = await plan_searches(topic)

        # Step 2: Searching
        await task_manager.update_task(
            task_id,
            status="searching",
            current_step=f"Searching the web ({len(search_plan.searches)} queries)...",
            percent=30
        )
        search_results = await perform_searches_with_progress(search_plan, task_id, task_manager)

        # Step 3: Writing
        await task_manager.update_task(
            task_id,
            status="writing",
            current_step="Generating comprehensive report...",
            percent=70
        )
        result = await write_report(topic, search_results)

        # Step 4: Complete
        await task_manager.update_task(
            task_id,
            status="completed",
            current_step="Complete!",
            percent=100,
            result=result.markdown_report
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        await task_manager.update_task(
            task_id,
            status="failed",
            current_step="Failed",
            percent=0,
            error=str(e)
        )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


@app.post("/cache/clear")
async def clear_cache():
    """Clear the entire cache"""
    await cache.clear()
    return {"status": "cache cleared"}


@app.get("/rate-limit/stats")
async def rate_limit_stats():
    """Get rate limiter statistics"""
    return rate_limiter.get_stats()


@app.get("/circuit-breakers")
async def circuit_breakers_status():
    """Get status of all circuit breakers"""
    from utils.retry import get_all_breaker_states
    return get_all_breaker_states()


# Periodic cleanup task
@app.on_event("startup")
async def startup_event():
    """Start background cleanup tasks"""

    async def cleanup_loop():
        while True:
            await asyncio.sleep(600)  # Every 10 minutes

            # Cleanup old tasks
            removed_tasks = task_manager.cleanup_old_tasks(max_age_minutes=60)
            if removed_tasks > 0:
                print(f"Cleaned up {removed_tasks} old tasks")

            # Cleanup expired cache entries
            removed_cache = await cache.cleanup_expired()
            if removed_cache > 0:
                print(f"Cleaned up {removed_cache} expired cache entries")

    asyncio.create_task(cleanup_loop())
