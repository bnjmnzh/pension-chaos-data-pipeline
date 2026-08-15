import json
import logging
import uuid
import httpx
import psycopg

# Configuration
GENERATOR_URL = "http://localhost:8000/api/v1/members/generate"
POSTGRES_DSN = "postgresql://user:password@localhost:5432/pension_platform"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def fetch_synthetic_batch(count: int = 10, chaos_drift: float = 0.1) -> list[dict]:
    """Fetch raw batch payload from FastAPI Generator."""
    payload = {
        "count": count,
        "chaos": {
            "drift_rate": chaos_drift,
            "null_rate": 0.05,
            "outlier_rate": 0.05,
            "duplicate_rate": 0.0,
        },
    }
    
    response = httpx.post(GENERATOR_URL, json=payload, timeout=10.0)
    response.raise_for_status()
    return response.json()["data"]


def load_raw_to_postgres(records: list[dict]):
    """Insert raw JSON records into raw.members table in Postgres."""
    batch_id = str(uuid.uuid4())
    
    with psycopg.connect(POSTGRES_DSN) as conn:
        with conn.cursor() as cur:
            rows = [(batch_id, json.dumps(record)) for record in records]
            
            cur.executemany(
                """
                INSERT INTO raw.members (batch_id, payload)
                VALUES (%s, %s::jsonb);
                """,
                rows,
            )
        conn.commit()
        
    logging.info(f"Successfully landed {len(records)} raw records into Postgres under Batch ID: {batch_id}")


if __name__ == "__main__":
    logging.info("Starting Bronze Ingestion Job...")
    try:
        data = fetch_synthetic_batch(count=20, chaos_drift=0.2)
        load_raw_to_postgres(data)
    except Exception as e:
        logging.error(f"Ingestion failed: {e}", exc_info=True)