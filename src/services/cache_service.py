import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from redis.asyncio import Redis
from redis.commands.search.field import VectorField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

class SemanticCache:
    def __init__(self, redis_client: Redis, threshold: float = 0.85):
        self.redis = redis_client
        self.threshold = threshold  # Optimized to 0.85 for production text matching
        self.index_name = "idx:prompts"
        print("Loading ML Embedding Model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_dimensions = 384

    def _normalize_text(self, text: str) -> str:
        """Production Guardrail: Clean text so punctuation or casing doesn't ruin matches."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Removes question marks, periods, commas
        return text

    async def setup_index(self):
        try:
            await self.redis.ft(self.index_name).info()
        except Exception:
            schema = (
                TextField("prompt"),
                TextField("response"),
                VectorField("embedding", "FLAT", {
                    "TYPE": "FLOAT32", 
                    "DIM": self.vector_dimensions, 
                    "DISTANCE_METRIC": "COSINE"
                })
            )
            definition = IndexDefinition(prefix=["cache:"], index_type=IndexType.HASH)
            await self.redis.ft(self.index_name).create_index(fields=schema, definition=definition)
            print("Redis Vector Index verified!")

    def _get_embedding(self, text: str) -> np.ndarray:
        cleaned_text = self._normalize_text(text)
        return self.model.encode(cleaned_text).astype(np.float32)

    async def get_cached_response(self, prompt: str):
        vector = self._get_embedding(prompt)
        query = Query("*=>[KNN 1 @embedding $vec AS score]") \
            .return_fields("prompt", "response", "score") \
            .sort_by("score") \
            .dialect(2)
        
        params = {"vec": vector.tobytes()}
        results = await self.redis.ft(self.index_name).search(query, params)
        
        if results.docs:
            distance = float(results.docs[0].score)
            similarity = 1.0 - distance
            
            # Safely decode bytes from Redis back to Python strings
            matched_prompt = results.docs[0].prompt
            if isinstance(matched_prompt, bytes):
                matched_prompt = matched_prompt.decode('utf-8')
                
            cached_response = results.docs[0].response
            if isinstance(cached_response, bytes):
                cached_response = cached_response.decode('utf-8')

            print(f"DEBUG | User: '{prompt}' vs Match: '{matched_prompt}' | Mathematical Score: {similarity:.4f}")

            if similarity >= self.threshold:
                return {
                    "similarity_score": round(similarity, 4),
                    "original_prompt": matched_prompt,
                    "response": cached_response
                }
        return None

    async def set_cache(self, prompt: str, response: str):
        vector = self._get_embedding(prompt)
        # Use a safe string key instead of python hash() which changes on every restart
        safe_key = re.sub(r'\s+', '_', self._normalize_text(prompt))[:50]
        key = f"cache:{safe_key}"
        
        mapping = {
            "prompt": prompt,
            "response": response,
            "embedding": vector.tobytes()
        }
        await self.redis.hset(key, mapping=mapping)
        await self.redis.expire(key, 86400)