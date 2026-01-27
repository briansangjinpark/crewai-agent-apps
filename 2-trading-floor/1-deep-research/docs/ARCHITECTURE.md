# Architecture Documentation

## System Overview

The Deep Research Agent is a production-ready multi-agent system built with modern async Python and React, featuring real-time progress tracking, intelligent caching, and enterprise-grade reliability.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                          │
│                        (Next.js Frontend)                        │
│  ┌──────────┐  ┌─────────────────┐  ┌────────────────────┐    │
│  │  Input   │  │  Progress Bar   │  │  Report Display    │    │
│  │  Form    │  │  (Real-time)    │  │  (Markdown)        │    │
│  └──────────┘  └─────────────────┘  └────────────────────┘    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/SSE
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    API Layer (api.py)                    │   │
│  │                                                           │   │
│  │  POST /research          SSE /research/{id}/stream       │   │
│  │  GET  /cache/stats       GET /circuit-breakers           │   │
│  └────────────┬─────────────────────────┬───────────────────┘   │
│               │                         │                        │
│  ┌────────────▼─────────┐  ┌───────────▼──────────┐            │
│  │    Middleware        │  │   Background Tasks   │            │
│  │  ┌───────────────┐   │  │  ┌────────────────┐  │            │
│  │  │ CORS          │   │  │  │ Task Manager   │  │            │
│  │  │ Rate Limiter  │   │  │  │ (In-memory)    │  │            │
│  │  └───────────────┘   │  │  └────────────────┘  │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Core Services                               │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │   │
│  │  │   Cache     │  │ Task Manager │  │ Retry Handler │  │   │
│  │  │  (LRU TTL)  │  │   (SSE Pub)  │  │   + Circuit   │  │   │
│  │  │             │  │              │  │    Breaker    │  │   │
│  │  └─────────────┘  └──────────────┘  └───────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│               RESEARCH WORKFLOW (main.py)                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Stage 1: PLANNING                                 │         │
│  │  ┌──────────────┐                                  │         │
│  │  │ Check Cache  │ → Cache Hit? → Return Plan       │         │
│  │  └──────┬───────┘                                  │         │
│  │         │ Cache Miss                                │         │
│  │         ↓                                           │         │
│  │  ┌──────────────────────────────────────┐          │         │
│  │  │  Planner Agent (gpt-4.1-mini)        │          │         │
│  │  │  + Retry Logic (max 3)               │          │         │
│  │  │  + Circuit Breaker                   │          │         │
│  │  └──────────────┬───────────────────────┘          │         │
│  │                 ↓                                   │         │
│  │  Generate 5 search queries + Cache result          │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Stage 2: SEARCHING (Parallel)                     │         │
│  │                                                      │         │
│  │  For each query:                                    │         │
│  │  ┌──────────────┐                                   │         │
│  │  │ Check Cache  │ → Cache Hit? → Return Result     │         │
│  │  └──────┬───────┘                                   │         │
│  │         │ Cache Miss                                 │         │
│  │         ↓                                            │         │
│  │  ┌──────────────────────────────────────┐           │         │
│  │  │  Search Agent (gpt-4.1-mini)         │           │         │
│  │  │  + WebSearchTool                     │           │         │
│  │  │  + Retry Logic (max 3)               │           │         │
│  │  │  + Circuit Breaker                   │           │         │
│  │  └──────────────┬───────────────────────┘           │         │
│  │                 ↓                                    │         │
│  │  Summarize results + Cache (TTL: 2h)                │         │
│  │                                                      │         │
│  │  [Run all 5 searches in parallel]                   │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                   │
│  ┌────────────────────────────────────────────────────┐         │
│  │  Stage 3: WRITING                                  │         │
│  │  ┌──────────────────────────────────────┐          │         │
│  │  │  Writer Agent (gpt-4o-mini)          │          │         │
│  │  │  + Retry Logic (max 3)               │          │         │
│  │  │  + Circuit Breaker                   │          │         │
│  │  └──────────────┬───────────────────────┘          │         │
│  │                 ↓                                   │         │
│  │  Generate comprehensive report (5-10 pages)        │         │
│  └────────────────────────────────────────────────────┘         │
│                                                                   │
│  Progress updates sent via Task Manager at each step             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ Real-time Updates
                            ↓
                    ┌───────────────┐
                    │ SSE Subscribers│
                    │  (Frontend)    │
                    └───────────────┘
```

---

## Component Details

### Frontend (Next.js + React)

**Components:**
- `page.tsx` - Main research input page with SSE integration
- `report/page.tsx` - Report display with markdown rendering
- `LoadingOverlay.tsx` - Progress indicator component
- `useResearchStream.ts` - Custom hook for SSE connections

**Technologies:**
- Next.js 14 with App Router
- Server-Sent Events (EventSource API)
- TailwindCSS for styling
- Lucide React for icons

### Backend (FastAPI + Python)

**API Layer:**
- FastAPI with async support
- CORS middleware for cross-origin requests
- Rate limiting middleware (10 req/min per IP)
- SSE via sse-starlette

**Core Services:**

**1. Task Manager (`core/task_manager.py`)**
- In-memory task state storage
- Publisher-subscriber pattern for SSE
- Automatic cleanup of old tasks (60 min)

**2. Cache (`core/cache.py`)**
- LRU eviction with TTL
- Thread-safe with asyncio locks
- Statistics tracking (hits, misses, hit rate)
- Automatic expiration cleanup

**3. Retry Handler (`utils/retry.py`)**
- Exponential backoff (2s → 4s → 8s → 10s max)
- Circuit breaker pattern per agent
- Failure threshold: 5 failures
- Recovery timeout: 60 seconds

**4. Rate Limiter (`api/middleware/rate_limit.py`)**
- Token bucket algorithm
- Sliding window per client IP
- Returns 429 with Retry-After header

### Agent Layer

**Planner Agent (`planner_agent.py`)**
- Model: gpt-4.1-mini
- Input: User query
- Output: List of 5 search queries with reasoning
- Cache: 1 hour TTL

**Search Agent (`search_agent.py`)**
- Model: gpt-4.1-mini
- Tools: WebSearchTool (low context)
- Input: Search query + reason
- Output: 2-3 paragraph summary
- Cache: 2 hour TTL
- Parallel execution

**Writer Agent (`writer_agent.py`)**
- Model: gpt-4o-mini
- Input: Original query + search summaries
- Output: Comprehensive report (5-10 pages, 1000+ words)
- No cache (reports are unique)

---

## Data Flow

### First Request (Cache Miss)

```
User Query: "What is quantum computing?"
    │
    ├─ Planning (2-3s)
    │   └─ LLM Call → 5 queries → Cache
    │
    ├─ Searching (10-15s)
    │   ├─ Query 1: LLM + Web → Cache
    │   ├─ Query 2: LLM + Web → Cache
    │   ├─ Query 3: LLM + Web → Cache
    │   ├─ Query 4: LLM + Web → Cache
    │   └─ Query 5: LLM + Web → Cache
    │
    └─ Writing (5-8s)
        └─ LLM Call → Report

Total: ~17-26 seconds
```

### Subsequent Request (Cache Hit)

```
User Query: "What is quantum computing?" (again)
    │
    ├─ Planning (~0.01s)
    │   └─ Cache Hit → Return Plan
    │
    ├─ Searching (~0.05s)
    │   ├─ Query 1: Cache Hit
    │   ├─ Query 2: Cache Hit
    │   ├─ Query 3: Cache Hit
    │   ├─ Query 4: Cache Hit
    │   └─ Query 5: Cache Hit
    │
    └─ Writing (5-8s)
        └─ LLM Call → Report

Total: ~5-8 seconds (70% faster)
```

---

## Reliability Features

### Retry Logic

```python
Attempt 1: Call agent
    ↓ Fails
Wait 2 seconds
    ↓
Attempt 2: Call agent
    ↓ Fails
Wait 4 seconds
    ↓
Attempt 3: Call agent
    ↓ Fails
Wait 8 seconds
    ↓
Attempt 4: Call agent
    ↓ Success or Final Failure
```

### Circuit Breaker States

```
         Normal Operation
              (CLOSED)
                 │
        5 consecutive failures
                 │
                 ↓
         Circuit Opens (OPEN)
         All requests fail fast
                 │
           Wait 60 seconds
                 │
                 ↓
         Try Recovery (HALF-OPEN)
                 │
        ┌────────┴────────┐
        │                 │
   Success           Failure
        │                 │
        ↓                 ↓
   Close Circuit    Open Circuit
     (CLOSED)         (OPEN)
```

### Rate Limiting

```
Client: 127.0.0.1
    │
Request 1  ✓ (9 remaining)
Request 2  ✓ (8 remaining)
Request 3  ✓ (7 remaining)
    ...
Request 10 ✓ (0 remaining)
Request 11 ✗ 429 Too Many Requests
           Retry-After: 45 seconds
```

---

## Performance Characteristics

### Latency

| Operation | First Request | Cached Request |
|-----------|--------------|----------------|
| Planning | 2-3s | 0.01s |
| Search (x5) | 10-15s | 0.05s |
| Writing | 5-8s | 5-8s |
| **Total** | **17-26s** | **5-8s** |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Cache (1000 items) | ~50-100 MB |
| Task Manager (10 active) | ~5 MB |
| Rate Limiter | ~1 MB |
| Agent Processes | ~200-300 MB |
| **Total** | **~250-400 MB** |

### Throughput

- Concurrent research tasks: 10+
- Requests per minute (rate limited): 10 per client
- Cache hit rate: 70-80% typical

---

## Technology Stack

### Backend
- **Python 3.11+** - Modern async Python
- **FastAPI** - High-performance web framework
- **Pydantic** - Data validation
- **sse-starlette** - Server-Sent Events
- **Anthropic Agents SDK** - AI agent framework

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Utility-first CSS
- **Lucide React** - Icon library

### External Services
- **OpenAI API** - LLM provider
- **Web Search** - Via Agents SDK

---

## Security Considerations

### Implemented
- ✅ CORS with whitelist
- ✅ Rate limiting per client IP
- ✅ Input validation (Pydantic)
- ✅ Error messages don't leak internals

### Recommended for Production
- [ ] API key authentication
- [ ] HTTPS/TLS encryption
- [ ] Request signing
- [ ] SQL injection prevention (if DB added)
- [ ] Content Security Policy headers
- [ ] DDoS protection
- [ ] Audit logging

---

## Scalability

### Current Design (Single Instance)
- Handles 10+ concurrent research tasks
- In-memory cache (1000 items)
- No database required

### Scaling Horizontally

**Add Redis for Shared Cache:**
```python
# Replace in-memory cache with Redis
import redis.asyncio as redis
cache_client = redis.from_url("redis://localhost:6379")
```

**Add PostgreSQL for Persistence:**
```sql
CREATE TABLE research_reports (
    id UUID PRIMARY KEY,
    topic TEXT,
    report TEXT,
    created_at TIMESTAMP
);
```

**Load Balancer:**
```
    Load Balancer
         │
    ┌────┴────┐
    │         │
Backend 1  Backend 2
    │         │
    └────┬────┘
         │
    Redis Cache
         │
   PostgreSQL
```

---

## Monitoring & Observability

### Available Metrics

```bash
# Cache performance
GET /cache/stats
{
  "hit_rate": "73.2%",
  "size": 45,
  "utilization": "4.5%"
}

# Circuit breaker health
GET /circuit-breakers
{
  "planner": {"is_open": false, "failure_count": 0},
  "searcher": {"is_open": false, "failure_count": 0},
  "writer": {"is_open": false, "failure_count": 0}
}

# Rate limiting
GET /rate-limit/stats
{
  "active_clients": 5,
  "total_requests_last_minute": 23
}
```

### Recommended Additions

- Prometheus metrics export
- Structured logging (JSON)
- Distributed tracing (OpenTelemetry)
- Error tracking (Sentry)
- Performance monitoring (DataDog/New Relic)

---

## Design Decisions

### Why In-Memory Cache?
- Simplicity - no external dependencies
- Low latency - sub-millisecond access
- Sufficient for single-instance deployment
- Easy to upgrade to Redis later

### Why SSE over WebSockets?
- Simpler - HTTP-based, works through proxies
- Unidirectional - perfect for progress updates
- Auto-reconnect - browser handles this
- Lower overhead - less connection management

### Why Circuit Breakers?
- Fail fast - don't waste time on unavailable services
- Prevent cascading failures - protect downstream
- Automatic recovery - no manual intervention

### Why Separate Agents?
- Separation of concerns - each agent has one job
- Specialized models - use best model for each task
- Independent scaling - can run on different instances
- Easier testing - test each agent independently

---

## Future Enhancements

### Short Term
- [ ] Add Redis for distributed cache
- [ ] Implement report streaming (chunks)
- [ ] Add Prometheus metrics
- [ ] Support multiple LLM providers

### Long Term
- [ ] Add PostgreSQL for persistence
- [ ] Implement report versioning
- [ ] Add collaborative features (share reports)
- [ ] Support custom agent configurations
- [ ] Add RAG for domain-specific knowledge

---

**Questions or suggestions?** See the main [README.md](../README.md) for contact info.
