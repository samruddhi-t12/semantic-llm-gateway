import pytest
import redis.asyncio as aioredis
from src.api.dependencies import verify_rate_limit

class MockClient:
    host = "127.0.0.1"

class MockRequest:
    def __init__(self, redis_client):
        self.client = MockClient()
        self.app = type('App', (), {'state': type('State', (), {'redis': redis_client})})

@pytest.mark.asyncio
async def test_rate_limiter_allows_and_blocks():
    redis_client = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    await redis_client.flushdb()
    
    request = MockRequest(redis_client=redis_client)
    
    client_id = await verify_rate_limit(request=request, api_key=None)
    
    assert client_id == "127.0.0.1"
    
    await redis_client.aclose()
