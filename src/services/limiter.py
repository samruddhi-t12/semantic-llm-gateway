import time
from typing import Tuple
from redis.asyncio import Redis

TOKEN_BUCKET_LUA = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = 1

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if not tokens then
    tokens = capacity
    last_refill = now
end

local time_passed = math.max(0, now - last_refill)
local replenished = time_passed * refill_rate
tokens = math.min(capacity, tokens + replenished)

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) * 2)
    return {1, tokens}
else
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', last_refill)
    return {0, tokens}
end
"""

class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.script = self.redis.register_script(TOKEN_BUCKET_LUA)

    async def is_allowed(self, identifier: str, capacity: int = 10, refill_rate: float = 2.0) -> Tuple[bool, float]:
        key = f"rate_limit:{identifier}"
        now = time.time()
        
        result = await self.script(
            keys=[key], 
            args=[capacity, refill_rate, now]
        )
        
        return bool(result[0]), float(result[1])