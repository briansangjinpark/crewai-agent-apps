# Quick Start Guide

Get the Deep Research Agent running in 5 minutes.

## Step 1: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 3: Start the Backend

```bash
uvicorn api:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Step 4: Install Frontend Dependencies

In a new terminal:

```bash
cd frontend
npm install
```

## Step 5: Start the Frontend

```bash
npm run dev
```

You should see:
```
- Local:        http://localhost:3000
```

## Step 6: Test It Out!

1. Open http://localhost:3000 in your browser
2. Enter a research query: "Latest developments in AI agents"
3. Watch the real-time progress
4. View your comprehensive report!

---

## Verify Installation

Test the backend:
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"ok"}
```

Test the cache:
```bash
curl http://127.0.0.1:8000/cache/stats
# Should return cache statistics
```

---

## Run Tests

Verify everything works:

```bash
python3 tests/test_cache.py
python3 tests/test_reliability.py
```

Both should show: ✅ All tests passed!

---

## Common Issues

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Make sure you're in the project root directory

**Frontend won't start**
- Check that Node.js 18+ is installed: `node --version`
- Delete `node_modules` and run `npm install` again

**Backend errors**
- Verify your `.env` file has a valid `OPENAI_API_KEY`
- Check that port 8000 isn't already in use

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [tests/README.md](tests/README.md) for testing info
- Customize agents in `*_agent.py` files
- Adjust configuration in `research_config.py`

**Happy researching! 🚀**
