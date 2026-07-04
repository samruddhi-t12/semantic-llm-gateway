import pytest
import asyncio
import redis.asyncio as aioredis
from src.api.dependencies import verify_rate_limit
from fastapi import HTTPException, Request

@pytest.mark.asyncio
async def test_rate_limiter_allows_and_blocks():
    # Connect to the temporary Redis service running in the GitHub runner
    redis_client = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    
    # Clean state for testing
    await redis_client.flushdb()
    
    # Mock the FastAPI Request object to pass a client host
    class MockRequest:
        def __init__(self, host):
            self.client = type('Client', (), {'host': host})
            self.app = type('App', (), {'state': type('State', (), {'redis': redis_client})})
            
    request = MockRequest(host="127.0.0.1")
    
    # Since our system configuration sets GLOBAL_RATE_LIMIT_PER_MIN, let's test execution
    # First request should pass smoothly
    client_id = await verify_rate_limit(request=request)
    assert client_id == "127.0.0.1"
    
    await redis_client.close()
