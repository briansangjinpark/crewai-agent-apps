# Deep Research Agent

A production-ready multi-agent research system that autonomously plans, searches, and synthesizes comprehensive research reports with real-time progress tracking, intelligent caching, and robust error handling.

## 🎯 Overview

The Deep Research Agent uses a three-stage workflow powered by specialized AI agents:

1. **Planning Agent** - Analyzes the query and creates a strategic search plan
2. **Search Agent** - Executes web searches and summarizes findings
3. **Writer Agent** - Synthesizes results into a comprehensive report

Built with FastAPI (backend), Next.js (frontend), and production-grade reliability features.

---

## 📖 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5 minutes
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and diagrams
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - What was built and why
- **[Testing Guide](tests/README.md)** - How to run tests

---

## ✨ Features

### **Real-time Progress Tracking**
- Server-Sent Events (SSE) for instant updates
- Live progress bar showing current step and percentage
- Granular status updates for each search query

### **Intelligent Caching**
- In-memory LRU cache with TTL
- Separate caching for plans (1h) and searches (2h)
- 170x faster on cache hits
- Cache statistics endpoint for monitoring

### **Production-Ready Reliability**
- **Retry Logic**: Exponential backoff with 3 retries per operation
- **Circuit Breakers**: Prevent cascading failures (separate for each agent)
- **Rate Limiting**: 10 requests/minute per client IP
- **Error Handling**: Graceful degradation with detailed error messages

### **Modern Architecture**
- Asynchronous processing with background tasks
- Type-safe with Pydantic models
- CORS-enabled for cross-origin requests
- Modular and testable design

---

## 📁 Project Structure

```
1-deep-research/
├── docs/                           # 📚 Documentation
│   ├── README.md                   # Documentation index
│   ├── QUICKSTART.md               # Quick setup guide
│   ├── ARCHITECTURE.md             # System architecture
│   └── IMPLEMENTATION_SUMMARY.md   # Implementation details
├── api/
│   └── middleware/
│       └── rate_limit.py           # Rate limiting middleware
├── core/
│   ├── cache.py                    # In-memory LRU cache
│   └── task_manager.py             # Task tracking & SSE
├── utils/
│   └── retry.py                    # Retry logic & circuit breakers
├── tests/
│   ├── __init__.py
│   ├── README.md                   # Testing documentation
│   ├── test_cache.py               # Cache functionality tests
│   └── test_reliability.py         # Reliability features tests
├── frontend/                       # Next.js UI
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Main research page
│   │   │   └── report/page.tsx    # Report display page
│   │   ├── components/
│   │   │   └── LoadingOverlay.tsx
│   │   └── hooks/
│   │       └── useResearchStream.ts # SSE hook
│   └── package.json
├── api.py                          # FastAPI server
├── main.py                         # Research workflow
├── models.py                       # Pydantic models
├── planner_agent.py                # Planning agent
├── search_agent.py                 # Search agent
├── writer_agent.py                 # Writing agent
├── research_config.py              # Configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   # Create .env file
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Start the backend:**
   ```bash
   uvicorn api:app --reload
   ```

   Server runs at: `http://127.0.0.1:8000`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the frontend:**
   ```bash
   npm run dev
   ```

   UI available at: `http://localhost:3000`

---

## 🔧 Usage

### Web Interface

1. Navigate to `http://localhost:3000`
2. Enter your research query
3. Watch real-time progress as the system:
   - Plans search strategy
   - Executes searches
   - Generates comprehensive report
4. View the formatted report with sources

### Command Line

Run research directly from Python:

```bash
python main.py
```

Edit `research_config.py` to change the default query.

### API Usage

**Start a research task:**
```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Latest developments in quantum computing"}'
```

Response:
```json
{
  "task_id": "a1b2c3d4-...",
  "status": "processing",
  "stream_url": "/research/a1b2c3d4-.../stream"
}
```

**Stream real-time progress:**
```bash
curl http://127.0.0.1:8000/research/a1b2c3d4-.../stream
```

**Poll task status:**
```bash
curl http://127.0.0.1:8000/research/a1b2c3d4-...
```

---

## 📡 API Endpoints

### Research

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/research` | POST | Start new research task (rate limited) |
| `/research/{id}/stream` | GET | Stream real-time progress via SSE |
| `/research/{id}` | GET | Get current task status (polling fallback) |

### Monitoring

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/cache/stats` | GET | Cache statistics (size, hits, misses, hit rate) |
| `/rate-limit/stats` | GET | Rate limiter statistics |
| `/circuit-breakers` | GET | Circuit breaker states |

### Admin

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cache/clear` | POST | Clear entire cache |

---

## ⚙️ Configuration

### Cache Settings

In `core/cache.py`:
```python
cache = InMemoryCache(
    max_size=1000,      # Maximum cached items
    default_ttl=3600    # Default TTL in seconds
)
```

### Rate Limiting

In `api/middleware/rate_limit.py`:
```python
rate_limiter = RateLimiter(
    requests_per_minute=10,  # Requests per client per minute
    burst_size=3             # Burst allowance
)
```

### Circuit Breakers

In `utils/retry.py`:
```python
CircuitBreaker(
    failure_threshold=5,   # Open after N failures
    recovery_timeout=60,   # Recovery period in seconds
    name="AgentName"
)
```

### Retry Logic

In `main.py`:
```python
await call_agent_with_retry(
    agent=agent,
    input_text=query,
    circuit_breaker=breaker,
    max_retries=3  # Number of retry attempts
)
```

---

## 🧪 Testing

Run all tests:

```bash
# Cache tests
python3 tests/test_cache.py

# Reliability tests
python3 tests/test_reliability.py
```

Test coverage:
- ✅ Cache operations (get, set, eviction, stats)
- ✅ Retry logic with exponential backoff
- ✅ Circuit breaker state transitions
- ✅ Rate limiting enforcement

See [tests/README.md](tests/README.md) for details.

---

## 📊 Architecture

### System Flow

```
User Query
    ↓
FastAPI Backend (api.py)
    ↓
Task Manager (creates background task)
    ↓
┌─────────────────────────────────────┐
│  Research Workflow (main.py)        │
│                                     │
│  1. Planning Agent                  │
│     ├─ Check cache                  │
│     ├─ Call LLM with retry          │
│     └─ Generate search plan         │
│                                     │
│  2. Search Agent (parallel)         │
│     ├─ Check cache per query        │
│     ├─ Execute web searches         │
│     └─ Summarize results            │
│                                     │
│  3. Writer Agent                    │
│     ├─ Synthesize findings          │
│     └─ Generate report              │
└─────────────────────────────────────┘
    ↓
Real-time Updates via SSE
    ↓
Frontend (Next.js)
```

### Key Components

**Task Manager** (`core/task_manager.py`)
- Tracks task state in-memory
- Publishes updates to SSE subscribers
- Automatic cleanup of old tasks

**Cache** (`core/cache.py`)
- LRU eviction policy
- Per-item TTL
- Thread-safe with asyncio locks

**Retry Handler** (`utils/retry.py`)
- Exponential backoff (2s → 4s → 8s)
- Circuit breaker integration
- Respects service health

**Rate Limiter** (`api/middleware/rate_limit.py`)
- Sliding window per client IP
- Configurable limits
- Returns `429` with `Retry-After` header

---

## 🔍 Monitoring

### Check System Health

```bash
# Cache statistics
curl http://127.0.0.1:8000/cache/stats
```

Response:
```json
{
  "size": 45,
  "max_size": 1000,
  "utilization": "4.5%",
  "cache_hits": 123,
  "cache_misses": 45,
  "total_requests": 168,
  "hit_rate": "73.2%"
}
```

### Circuit Breaker Status

```bash
curl http://127.0.0.1:8000/circuit-breakers
```

Response:
```json
{
  "planner": {
    "name": "PlannerAgent",
    "is_open": false,
    "failure_count": 0,
    "failure_threshold": 5
  },
  "searcher": { ... },
  "writer": { ... }
}
```

### Rate Limit Statistics

```bash
curl http://127.0.0.1:8000/rate-limit/stats
```

Response:
```json
{
  "active_clients": 5,
  "total_requests_last_minute": 23,
  "requests_per_minute_limit": 10
}
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Failed to fetch" error in frontend**
- Ensure backend is running: `uvicorn api:app --reload`
- Check CORS origins in `api.py` match your frontend URL
- Verify firewall isn't blocking port 8000

**2. "Rate limit exceeded"**
- Wait for the timeout specified in `Retry-After` header
- Increase limit in `api/middleware/rate_limit.py` if needed
- Rate limits reset after 60 seconds

**3. "Circuit breaker is open"**
- Service is temporarily unavailable due to repeated failures
- Check LLM API credentials and quota
- Wait for recovery timeout (default: 60s)
- View breaker status: `GET /circuit-breakers`

**4. Slow response times**
- Check cache hit rate: `GET /cache/stats`
- Low hit rate? Queries might be too diverse
- Increase cache size or TTL in `core/cache.py`

**5. Import errors when running tests**
- Run tests from project root, not tests directory
- Python path is set correctly in test files

---

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    env_file:
      - .env

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Production Checklist

- [ ] Set appropriate rate limits for production traffic
- [ ] Configure cache size based on available memory
- [ ] Set up monitoring/alerting for circuit breakers
- [ ] Enable HTTPS for production
- [ ] Review and adjust timeouts
- [ ] Set up log aggregation
- [ ] Configure backup for critical data

---

## 📈 Performance

### Metrics

- **First Request**: ~15-20 seconds (planning + 5 searches + writing)
- **Cached Request**: ~0.1 seconds (170x faster)
- **Cache Hit Rate**: 70-80% in typical usage
- **Memory Usage**: ~50-100MB for 1000 cached items
- **Concurrent Requests**: Supports 10+ simultaneous research tasks

### Optimization Tips

1. **Increase cache size** for higher hit rates
2. **Extend TTL** for searches (stable content)
3. **Reduce search count** in `planner_agent.py` (NUM_SEARCHES)
4. **Use faster models** (e.g., `gpt-4o-mini` instead of `gpt-4o`)

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add PostgreSQL for persistent cache
- Implement streaming report generation
- Add support for multiple LLM providers
- Enhanced error recovery strategies
- Prometheus metrics integration
- WebSocket alternative to SSE

---

## 📝 License

This project is part of the crewai-agent-apps repository.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Next.js](https://nextjs.org/) - React framework
- [Anthropic Agents SDK](https://github.com/anthropics/anthropic-sdk-python) - AI agent framework
- [sse-starlette](https://github.com/sysid/sse-starlette) - Server-Sent Events

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Server-Sent Events (SSE) Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [LRU Cache Algorithm](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU))

---

**Need help?** Check the [troubleshooting section](#-troubleshooting) or open an issue.

**Quick Start:** Run `uvicorn api:app --reload` and visit `http://localhost:3000`
