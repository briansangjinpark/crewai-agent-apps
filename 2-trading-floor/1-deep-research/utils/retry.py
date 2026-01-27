"""
Retry logic and circuit breaker for resilient agent calls
"""
import time
import asyncio
from typing import Optional, Any
from functools import wraps


class CircuitBreaker:
    """
    Circuit breaker pattern to prevent cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail immediately
    - HALF_OPEN: Recovery period, test if service is back
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "CircuitBreaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.is_open = False

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        # Check if circuit is open
        if self.is_open:
            if self.last_failure_time and time.time() - self.last_failure_time < self.recovery_timeout:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is open. "
                    f"Service temporarily unavailable. Try again in "
                    f"{int(self.recovery_timeout - (time.time() - self.last_failure_time))}s"
                )
            else:
                # Try to recover (half-open state)
                print(f"[{self.name}] Circuit breaker entering half-open state, testing service...")
                self.is_open = False

        try:
            result = await func(*args, **kwargs)
            # Success! Reset failure count
            self.failure_count = 0
            return result
        except Exception as e:
            # Record failure
            self.failure_count += 1
            self.last_failure_time = time.time()

            print(f"[{self.name}] Failure {self.failure_count}/{self.failure_threshold}: {str(e)[:100]}")

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.is_open = True
                print(f"[{self.name}] Circuit breaker opened after {self.failure_count} failures")

            raise e

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            "name": self.name,
            "is_open": self.is_open,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure": self.last_failure_time
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Global circuit breakers for each agent type
planner_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="PlannerAgent")
searcher_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="SearcherAgent")
writer_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="WriterAgent")


async def retry_with_backoff(
    func,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    **kwargs
):
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except CircuitBreakerOpenError:
            # Don't retry if circuit breaker is open
            raise
        except Exception as e:
            last_exception = e

            if attempt < max_retries:
                # Calculate delay with exponential backoff
                delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                print(f"[RETRY] Attempt {attempt + 1}/{max_retries + 1} failed: {str(e)[:100]}")
                print(f"[RETRY] Retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"[RETRY] All {max_retries + 1} attempts failed")

    # All retries exhausted
    raise last_exception


async def call_agent_with_retry(
    agent,
    input_text: str,
    circuit_breaker: CircuitBreaker,
    max_retries: int = 3
):
    """
    Call an agent with retry logic and circuit breaker protection.

    This is the primary function to use for all agent calls.
    """
    async def agent_call():
        from agents import Runner
        return await circuit_breaker.call(Runner.run, agent, input_text)

    return await retry_with_backoff(
        agent_call,
        max_retries=max_retries,
        initial_delay=2.0,
        max_delay=10.0
    )


def get_all_breaker_states() -> dict:
    """Get state of all circuit breakers"""
    return {
        "planner": planner_breaker.get_state(),
        "searcher": searcher_breaker.get_state(),
        "writer": writer_breaker.get_state()
    }
