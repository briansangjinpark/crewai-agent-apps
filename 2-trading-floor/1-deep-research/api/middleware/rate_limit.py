"""
Rate limiting middleware to prevent API abuse
"""
from collections import defaultdict
from typing import Dict, List
import time


class RateLimiter:
    """
    Token bucket rate limiter.

    Tracks requests per client IP and enforces rate limits.
    """

    def __init__(self, requests_per_minute: int = 10, burst_size: int = 3):
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.requests: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, client_id: str) -> tuple[bool, dict]:
        """
        Check if client has exceeded rate limit.

        Returns:
            (allowed, info) - tuple of whether request is allowed and rate limit info
        """
        now = time.time()
        minute_ago = now - 60

        # Clean old requests (older than 1 minute)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]

        # Count recent requests
        recent_requests = len(self.requests[client_id])

        # Check if limit exceeded
        if recent_requests >= self.requests_per_minute:
            remaining = 0
            retry_after = int(self.requests[client_id][0] - minute_ago)
            return False, {
                "allowed": False,
                "limit": self.requests_per_minute,
                "remaining": remaining,
                "retry_after": retry_after
            }

        # Allow request and record it
        self.requests[client_id].append(now)
        remaining = self.requests_per_minute - (recent_requests + 1)

        return True, {
            "allowed": True,
            "limit": self.requests_per_minute,
            "remaining": remaining,
            "reset": int(now - minute_ago + 60)
        }

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for a client"""
        now = time.time()
        minute_ago = now - 60
        recent = [r for r in self.requests[client_id] if r > minute_ago]
        return max(0, self.requests_per_minute - len(recent))

    def reset_client(self, client_id: str):
        """Reset rate limit for a specific client"""
        if client_id in self.requests:
            del self.requests[client_id]

    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        now = time.time()
        minute_ago = now - 60

        # Count active clients
        active_clients = 0
        total_requests = 0

        for client_id, requests in self.requests.items():
            recent = [r for r in requests if r > minute_ago]
            if recent:
                active_clients += 1
                total_requests += len(recent)

        return {
            "active_clients": active_clients,
            "total_requests_last_minute": total_requests,
            "requests_per_minute_limit": self.requests_per_minute
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=10, burst_size=3)
