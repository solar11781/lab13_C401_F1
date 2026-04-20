import argparse
import concurrent.futures
import json
import time
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
# QUERIES = Path("data/sample_queries.jsonl")
# QUERIES = Path("data/bank_sample_queries_200.jsonl")
QUERIES = Path("data/adversarial_queries.jsonl")


def send_request(client: httpx.Client, payload: dict, results: list) -> None:
    start = time.perf_counter()
    try:
        r = client.post(f"{BASE_URL}/chat", json=payload)
        latency = (time.perf_counter() - start) * 1000

        try:
            data = r.json()
        except Exception:
            data = {}

        correlation_id = data.get("correlation_id", "N/A")

        print(f"[{r.status_code}] {correlation_id} | {payload['feature']} | {latency:.1f}ms")

        results.append({
            "status": r.status_code,
            "latency_ms": latency,
            "correlation_id": correlation_id,
        })

    except Exception as e:
        latency = (time.perf_counter() - start) * 1000
        print(f"[ERROR] {e}")
        results.append({
            "status": "error",
            "latency_ms": latency,
            "correlation_id": None,
        })


def main() -> None:
    print("Starting load test...", flush=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()

    lines = [line for line in QUERIES.read_text(encoding="utf-8").splitlines() if line.strip()]

    results = []

    with httpx.Client(timeout=30.0) as client:
        for _ in range(args.repeat):
            if args.concurrency > 1:
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
                    futures = [
                        executor.submit(send_request, client, json.loads(line), results)
                        for line in lines
                    ]
                    concurrent.futures.wait(futures)
            else:
                for line in lines:
                    send_request(client, json.loads(line), results)

    # ---- Summary ----
    latencies = [r["latency_ms"] for r in results if r["status"] != "error"]
    errors = len([r for r in results if r["status"] == "error"])

    if latencies:
        latencies.sort()
        n = len(latencies)

        def p(x):
            return latencies[int(x * n)]

        print("\n--- SUMMARY ---")
        print(f"Total requests: {len(results)}")
        print(f"Errors: {errors}")
        print(f"Avg latency: {sum(latencies)/n:.2f} ms")
        print(f"P50: {p(0.5):.2f} ms")
        print(f"P95: {p(0.95):.2f} ms")
        print(f"P99: {p(0.99):.2f} ms")

if __name__ == "__main__":
    main()