from src.tasks.celery_app import celery
import time
import json

@celery.task(name="log_telemetry")
def log_telemetry_data(client_id: str, prompt: str, status: str, latency: str, similarity: float = None):
    """
    This function runs completely in the background. 
    In a real app, this would write to PostgreSQL or AWS CloudWatch.
    """
    # Simulate a slow database write operation
    time.sleep(1.5)
    
    log_entry = {
        "client_id": client_id,
        "prompt": prompt,
        "status": status,
        "latency": latency,
        "similarity_score": similarity
    }
    
    # We will just write it to a local file for demonstration
    with open("telemetry_logs.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    print(f"✅ [BACKGROUND WORKER] Telemetry saved for {client_id} | Status: {status}")
    return True