from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from src.core.config import settings
from src.api.v1 import gateway
from src.services.cache_service import SemanticCache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # decode_responses must be False here for the raw vector bytes to work
    app.state.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
    
    # Initialize the cache service and load the ML model EXACTLY ONCE at startup
    app.state.cache = SemanticCache(app.state.redis, threshold=settings.SEMANTIC_CACHE_THRESHOLD)
    await app.state.cache.setup_index()
    
    yield
    await app.state.redis.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(gateway.router, prefix="/api/v1", tags=["Gateway"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "project": settings.PROJECT_NAME
    }