# Semantic LLM Gateway

A distributed API gateway that proxies and secures Large Language Model (LLM) requests using per-client rate limiting, semantic caching, and asynchronous telemetry.

The project demonstrates practical backend engineering concepts including distributed systems, concurrency control, vector search, and scalable API design.

---

# Architecture

```text
                    Client
                       │
                       ▼
               FastAPI Gateway
                       │
      ┌────────────────┴────────────────┐
      ▼                                 ▼
Token Bucket                     Semantic Cache
Rate Limiter                (Redis + Embeddings)
      │                                 │
      └────────────────┬────────────────┘
                       ▼
             Downstream LLM Provider
                       │
                       ▼
         Celery + Redis Worker Queue
            (Asynchronous Telemetry)
```

---

# Why this Project Exists

Large Language Model APIs are both expensive and latency-sensitive.

This gateway addresses two common production challenges:

1. **Cost & Abuse Control**  
   A distributed token bucket rate limiter protects downstream APIs from excessive traffic while enforcing per-client quotas.

2. **Semantic Request Reuse**  
   Many prompts are semantically identical even when text differs. Using sentence embeddings and Redis vector search allows cached responses to be reused, significantly reducing latency and unnecessary LLM API calls.

---

# Key Features

## Semantic Vector Cache

Traditional caches only work for identical requests.

This gateway generates embeddings using **Sentence Transformers (`all-MiniLM-L6-v2`)** and stores them inside **Redis Stack**.

Incoming prompts are compared using cosine similarity.

If the similarity score exceeds the configured threshold, the cached response is returned immediately.

### Benefits

- Reduces redundant LLM API calls
- Improves response latency
- Lowers inference cost

---

## Atomic Token Bucket Rate Limiter

Implements a distributed token bucket algorithm using **Redis Lua Scripts**.

Since verification and token deduction occur atomically inside Redis, race conditions are prevented even under concurrent traffic.

---

## Asynchronous Telemetry

Telemetry collection is completely removed from the request path.

FastAPI immediately returns responses while **Celery** workers asynchronously process logging and analytics.

This keeps request latency low under heavy load.

---

# Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI, Python |
| Cache & Vector Search | Redis Stack |
| Async Processing | Celery |
| Machine Learning | HuggingFace Sentence Transformers, PyTorch |
| Infrastructure | Docker, Docker Compose |

---

# Project Structure

```text
semantic-llm-gateway/
│
├── src/
├── tests/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/samruddhi-t12/semantic-llm-gateway.git
cd semantic-llm-gateway
```

---

## Install Dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
APP_ENV=development
PROJECT_NAME=Semantic LLM Gateway

REDIS_URL=redis://127.0.0.1:6379/0

SEMANTIC_CACHE_THRESHOLD=0.85

GLOBAL_RATE_LIMIT_PER_MIN=60
```

---

## Start Infrastructure

```bash
docker compose up --build
```

---

## Run the Gateway

```bash
uvicorn src.main:app --reload
```

---

## Run the Celery Worker

```bash
celery -A src.tasks.celery_app worker --loglevel=info --pool=solo
```

---

# Testing

Run the complete test suite:

```bash
pytest -v
```

The test suite validates:

- Token Bucket Rate Limiter
- Concurrent request handling
- Semantic cache hit/miss logic
- Gateway endpoint behaviour

---

# Continuous Integration

GitHub Actions automatically runs the test suite on every push and pull request to the `main` branch.

The workflow:

- Installs project dependencies
- Executes the complete pytest suite
- Verifies project health before merging

---

# Example API

### Endpoint

```http
POST /api/v1/generate
```

### Example Response

```json
{
    "status": "cache_hit",
    "similarity": 0.8912,
    "latency": "15ms"
}
```

---

# Future Improvements

- Circuit Breaker for downstream LLM providers
- Warm-loaded embedding model for faster cold starts
- Usage dashboard with telemetry analytics
- Prometheus & Grafana monitoring
- Distributed tracing with OpenTelemetry

---

# Author

**Samruddhi Thorat**
