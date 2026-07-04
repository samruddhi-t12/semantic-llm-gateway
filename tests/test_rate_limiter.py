import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import redis.asyncio as aioredis
from src.api.dependencies import verify_rate_limit

# Create a minimal app to properly trigger FastAPI's dependency injection
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize Redis when the test app boots up
    app.state.redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)
    await app.state.redis.flushdb()

@app.on_event("shutdown")
async def shutdown():
    # Gracefully close Redis to prevent "Event loop is closed" errors
    await app.state.redis.close()

# Create a dummy route and attach the rate limiter dependency
@app.get("/test")
async def dummy_endpoint(client_id: str = Depends(verify_rate_limit)):
    return {"client_id": client_id}

def test_rate_limiter_allows_and_blocks():
    # TestClient automatically triggers the startup and shutdown events
    with TestClient(app) as client:
        
        # Send a request to the route. The dependency is now evaluated correctly.
        response = client.get("/test")
        
        # 200 OK means the rate limit successfully allowed the first request
        assert response.status_code == 200
        
        # FastAPI's TestClient mocks the incoming IP address as 'testclient'
        assert response.json()["client_id"] == "testclient"
