from fastapi import APIRouter, Depends, Request
import asyncio
from src.api.dependencies import verify_rate_limit
from src.tasks.workers import log_telemetry_data

router = APIRouter()

@router.post("/generate")
async def generate_ai_response(
    prompt: str, 
    request: Request,
    client_id: str = Depends(verify_rate_limit)
):
    cache = request.app.state.cache
    
    cached_data = await cache.get_cached_response(prompt)
    if cached_data:
        # Trigger Celery background task instantly (.delay)
        log_telemetry_data.delay(
            client_id=client_id, 
            prompt=prompt, 
            status="cache_hit", 
            latency="15ms",
            similarity=cached_data["similarity_score"]
        )
        
        return {
            "status": "cache_hit",
            "client_id": client_id,
            "prompt": prompt,
            "matched_prompt": cached_data["original_prompt"],
            "similarity": cached_data["similarity_score"],
            "response": cached_data["response"],
            "metrics": {"latency": "15ms"}
        }
    
    await asyncio.sleep(2.0)
    llm_response = f"This is the AI's complex answer to: '{prompt}'"
    await cache.set_cache(prompt, llm_response)
    
    # Trigger Celery background task for a miss
    log_telemetry_data.delay(
        client_id=client_id, 
        prompt=prompt, 
        status="cache_miss", 
        latency="2.0s"
    )
    
    return {
        "status": "cache_miss (computed)",
        "client_id": client_id,
        "prompt": prompt,
        "response": llm_response,
        "metrics": {"latency": "2.0s"}
    }