# Tests

This directory contains test scripts for the deep research module.

## Test Files

### test_cache.py
Tests the in-memory caching system.

**Tests:**
- Basic get/set operations
- Cache misses
- get_or_compute pattern
- Cache statistics
- Cache clearing

**Run:**
```bash
python3 tests/test_cache.py
```

### test_reliability.py
Tests reliability features including retry logic, circuit breakers, and rate limiting.

**Tests:**
- Retry logic with exponential backoff
- Circuit breaker pattern (CLOSED → OPEN → HALF-OPEN → CLOSED)
- Rate limiting enforcement

**Run:**
```bash
python3 tests/test_reliability.py
```

## Running All Tests

```bash
# From project root
python3 tests/test_cache.py
python3 tests/test_reliability.py
```

## Test Coverage

- ✅ Cache: get, set, get_or_compute, stats, clear, expiration
- ✅ Retry: exponential backoff, max retries, failure handling
- ✅ Circuit Breaker: state transitions, recovery timeout, failure threshold
- ✅ Rate Limiter: request tracking, limit enforcement, statistics
