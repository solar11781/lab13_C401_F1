import argparse
import httpx

BASE_URL = "http://127.0.0.1:8000"


def get_status():
    r = httpx.get(f"{BASE_URL}/health", timeout=10.0)
    print("Current incidents:", r.json().get("incidents"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=["rag_slow", "tool_fail", "cost_spike"])
    parser.add_argument("--disable", action="store_true")
    parser.add_argument("--status", action="store_true")

    args = parser.parse_args()

    if args.status:
        get_status()
        return

    if not args.scenario:
        print("Please provide --scenario or use --status")
        return

    path = f"/incidents/{args.scenario}/disable" if args.disable else f"/incidents/{args.scenario}/enable"

    r = httpx.post(f"{BASE_URL}{path}", timeout=10.0)
    print(r.status_code, r.json())

    # verify
    get_status()


if __name__ == "__main__":
    main()