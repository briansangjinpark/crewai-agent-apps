"""
Test script for reliability features (retry logic and circuit breaker)
"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from utils.retry import CircuitBreaker, retry_with_backoff, CircuitBreakerOpenError


async def test_retry_logic():
    """Test exponential backoff retry logic"""
    print("=" * 60)
    print("Test 1: Retry Logic with Exponential Backoff")
    print("=" * 60)

    attempt_count = 0

    async def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        print(f"Attempt {attempt_count}")
        if attempt_count < 3:
            raise Exception(f"Temporary failure {attempt_count}")
        return "Success!"

    try:
        result = await retry_with_backoff(
            flaky_function,
            max_retries=3,
            initial_delay=0.5,
            max_delay=2.0
        )
        print(f"✓ Result: {result}")
        print(f"✓ Total attempts: {attempt_count}")
        assert result == "Success!"
        assert attempt_count == 3
    except Exception as e:
        print(f"✗ Failed: {e}")
        raise

    print()


async def test_circuit_breaker():
    """Test circuit breaker pattern"""
    print("=" * 60)
    print("Test 2: Circuit Breaker")
    print("=" * 60)

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=2, name="TestBreaker")
    call_count = 0

    async def failing_function():
        nonlocal call_count
        call_count += 1
        raise Exception(f"Service error {call_count}")

    # Test failures until circuit opens
    print("\n1. Calling function until circuit opens...")
    for i in range(5):
        try:
            await breaker.call(failing_function)
        except CircuitBreakerOpenError as e:
            print(f"✓ Circuit opened: {str(e)[:80]}...")
            break
        except Exception:
            print(f"  Failure {i+1} recorded")

    # Verify circuit is open
    state = breaker.get_state()
    print(f"\n2. Circuit breaker state: {state}")
    assert state['is_open'] == True, "Circuit should be open"
    print("✓ Circuit is open")

    # Try to call while circuit is open
    print("\n3. Attempting to call while circuit is open...")
    try:
        await breaker.call(failing_function)
        print("✗ Should have raised CircuitBreakerOpenError")
        raise AssertionError("Circuit breaker should be open")
    except CircuitBreakerOpenError:
        print("✓ Circuit breaker blocked the call")

    # Wait for recovery timeout
    print("\n4. Waiting for recovery timeout...")
    await asyncio.sleep(2.5)

    # Circuit should try to recover (half-open state)
    print("\n5. Testing recovery (half-open state)...")

    async def working_function():
        return "Service recovered!"

    try:
        result = await breaker.call(working_function)
        print(f"✓ Circuit recovered: {result}")
        assert breaker.failure_count == 0, "Failure count should reset"
        assert breaker.is_open == False, "Circuit should be closed"
    except Exception as e:
        print(f"✗ Recovery failed: {e}")
        raise

    print()


async def test_rate_limiter():
    """Test rate limiter"""
    print("=" * 60)
    print("Test 3: Rate Limiter")
    print("=" * 60)

    # Import rate limiter directly from the module file
    import importlib.util
    rate_limit_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'api', 'middleware', 'rate_limit.py'
    )
    spec = importlib.util.spec_from_file_location("rate_limit", rate_limit_path)
    rate_limit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rate_limit)
    RateLimiter = rate_limit.RateLimiter

    limiter = RateLimiter(requests_per_minute=5, burst_size=2)
    client_id = "test_client"

    print("\n1. Making requests within limit...")
    for i in range(5):
        allowed, info = limiter.check_rate_limit(client_id)
        assert allowed == True, f"Request {i+1} should be allowed"
        print(f"  Request {i+1}: Allowed (remaining: {info['remaining']})")

    print("\n2. Exceeding rate limit...")
    allowed, info = limiter.check_rate_limit(client_id)
    assert allowed == False, "Request should be rate limited"
    print(f"✓ Rate limit enforced: {info}")
    print(f"  Retry after: {info['retry_after']}s")

    print("\n3. Checking stats...")
    stats = limiter.get_stats()
    print(f"  Active clients: {stats['active_clients']}")
    print(f"  Total requests: {stats['total_requests_last_minute']}")
    assert stats['active_clients'] >= 1
    print("✓ Rate limiter stats working")

    print()


async def main():
    """Run all reliability tests"""
    print("\n" + "=" * 60)
    print("RELIABILITY FEATURES TEST SUITE")
    print("=" * 60 + "\n")

    try:
        await test_retry_logic()
        await test_circuit_breaker()
        await test_rate_limiter()

        print("=" * 60)
        print("✅ ALL RELIABILITY TESTS PASSED!")
        print("=" * 60)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    asyncio.run(main())
