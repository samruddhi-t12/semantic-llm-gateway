# src/api/dependencies.py

from fastapi import Request, HTTPException, Security
from fastapi.security import APIKeyHeader
from src.services.limiter import RateLimiter
from redis.exceptions import ConnectionError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_rate_limit(request: Request, api_key: str = Security(api_key_header)):
    identifier = api_key if api_key else request.client.host
    
    redis_client = request.app.state.redis
    limiter = RateLimiter(redis_client)
    
    try:
        allowed, remaining = await limiter.is_allowed(identifier=identifier, capacity=5, refill_rate=1.0)
    except ConnectionError:
        print("WARNING: Redis server is offline. Bypassing Token Bucket rate limiter to prevent 500 Internal Server Error.")
        return identifier
    
    if not allowed:
        raise HTTPException(
            status_code=429, 
            detail="Rate Limit Exceeded. Your Token Bucket is empty. Please slow down."
        )
    
    return identifier