# Semantic LLM Gateway

An enterprise-grade API gateway designed to securely proxy, rate-limit, and semantically cache downstream Large Language Model (LLM) inference requests. 

This project bridges the gap between Machine Learning and Systems Engineering, demonstrating how to protect expensive AI microservices from traffic spikes while optimizing latency and compute costs using vector search.

## ✨ Core Architecture & Features

### 1. Semantic Vector Caching (Cost & Latency Optimization)
Standard caches fail when users rephrase questions. This gateway intercepts requests and uses a local **Sentence-Transformer (`all-MiniLM-L6-v2`)** to convert text into a 384-dimensional vector. 
* Uses **Redis Stack** to perform a K-Nearest Neighbor (KNN) Cosine Similarity search.
* If a prompt matches an existing cache with a `>0.85` similarity score, the gateway returns the cached LLM response.
* **Result:** Reduces redundant API call latency from ~2000ms to **~15ms** and saves downstream token costs.

### 2. Atomic Token Bucket Rate Limiting (Thundering Herd Defense)
Built a distributed rate limiter to defend against concurrent traffic spikes.
* Uses **Redis Lua Scripting** to ensure token verification and deduction happen as a strict, atomic transaction.
* Completely eliminates race conditions that standard Python-based rate limiters suffer from during massive concurrent requests.

### 3. Asynchronous Telemetry (Zero-Blocking Logging)
High-throughput systems cannot afford database write latency on the main thread.
* Integrated a **Celery Message Queue** backed by Redis.
* FastAPI instantly offloads telemetry data (IP, latency, similarity scores) to the message broker and returns the response to the user.
* Background worker processes handle heavy database/file I/O at their own pace, keeping the API event loop unblocked.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **Message Broker & Vector DB:** Redis Stack
* **Asynchronous Workers:** Celery
* **Machine Learning:** HuggingFace `sentence-transformers`, PyTorch, NumPy
* **Infrastructure:** Docker, Docker Compose

---

## 🚀 Local Setup & Installation

### Prerequisites
* Python 3.10+
* Docker Desktop

### 1. Clone & Install
```bash
git clone https://github.com/samruddhi-t12/semantic-llm-gateway.git
cd ai-inference-gateway
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```
### 2. Environment Variables
Create a .env file in the root directory:
```bash
APP_ENV=development
PROJECT_NAME="AI Inference Gateway"
LOG_LEVEL=info
REDIS_URL=redis://127.0.0.1:6379/0
SEMANTIC_CACHE_THRESHOLD=0.85
GLOBAL_RATE_LIMIT_PER_MIN=60
```
### 3. Boot the Infrastructure
Start the Redis Stack container (includes RediSearch for vector math):
```bash
docker-compose up -d redis-stack
```
### 4. Run the Gateway
You will need two separate terminal windows to run the API and the background worker.

Terminal 1 (FastAPI Server):
(Note: The ML embedding model will take a few seconds to download on the very first boot).
```bash
uvicorn src.main:app --reload
```
Terminal 2 (Celery Background Worker):
```bash
celery -A src.tasks.celery_app worker --loglevel=info --pool=solo
```
## ⚡ API Reference
### POST /api/v1/generate
Proxies the prompt to the AI model. Triggers rate limiting and semantic caching.

Request:
```bash
POST [http://127.0.0.1:8000/api/v1/generate?prompt=what%20is%20the%20capital%20of%20france](http://127.0.0.1:8000/api/v1/generate?prompt=what%20is%20the%20capital%20of%20france)
```
Response (Cache Hit Example):
```bash
{
  "status": "cache_hit",
  "client_id": "127.0.0.1",
  "prompt": "Tell me the French capital",
  "matched_prompt": "what is the capital of france",
  "similarity": 0.8912,
  "response": "This is the AI's complex answer to: 'what is the capital of france'",
  "metrics": {
    "latency": "15ms"
  }
}
```
