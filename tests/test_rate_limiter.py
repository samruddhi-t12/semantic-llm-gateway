import time
import threading
import pytest

from app.rate_limiter import TokenBucketRateLimiter  # adjust import to your actual path


def test_allows_requests_within_limit():
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1)
    for _ in range(5):
        assert limiter.allow_request(client_id="client-a") is True


def test_blocks_requests_beyond_capacity():
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1)
    for _ in range(3):
        assert limiter.allow_request(client_id="client-b") is True
    assert limiter.allow_request(client_id="client-b") is False


def test_refills_tokens_over_time():
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate=2)  # 2 tokens/sec
    limiter.allow_request(client_id="client-c")
    limiter.allow_request(client_id="client-c")
    assert limiter.allow_request(client_id="client-c") is False
    time.sleep(1.1)
    assert limiter.allow_request(client_id="client-c") is True


def test_thread_safety_under_concurrent_requests():
    limiter = TokenBucketRateLimiter(capacity=50, refill_rate=0)
    results = []
    lock = threading.Lock()

    def worker():
        allowed = limiter.allow_request(client_id="client-d")
        with lock:
            results.append(allowed)

    threads = [threading.Thread(target=worker) for _ in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 50  # exactly capacity, no race condition over-allowance
    assert results.count(False) == 50
