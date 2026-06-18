import asyncio
import httpx
import time

async def fire_request(client, request_id):
    start = time.time()
    response = await client.post("http://localhost:8000/api/v1/generate?prompt=hello")
    elapsed = time.time() - start
    
    if response.status_code == 200:
        print(f"✅ Request {request_id}: SUCCESS (Took {elapsed:.2f}s)")
    elif response.status_code == 429:
        print(f"🛑 Request {request_id}: BLOCKED 429 (Took {elapsed:.2f}s)")
    else:
        print(f"⚠️ Request {request_id}: Error {response.status_code}")

async def main():
    print("🚀 Firing 10 concurrent requests at the gateway...\n")
    # Added timeout=30.0 to prevent httpx.ReadTimeout exceptions
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [fire_request(client, i) for i in range(1, 11)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())