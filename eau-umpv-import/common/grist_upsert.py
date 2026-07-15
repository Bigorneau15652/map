"""Shared helper to upsert daily water-meter readings into the unified Grist
"Releves_Journaliers" table, and small env-var utilities. Used by every
per-site import script (import_suez_beziers.py, import_regie3m.py, ...) so
they all write in a single consistent schema.
"""
import os
import sys

import requests


def env(name: str, required: bool = True, default: str = None) -> str:
    # GitHub Actions sets env vars for unset secrets to "" rather than leaving
    # them unset, so treat blank the same as missing before applying default.
    value = os.environ.get(name) or default
    if required and not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


def push_records(server: str, doc_id: str, table_id: str, api_key: str, records: list) -> int:
    """Upsert records into a Grist table, matching each one on its `require` key."""
    if not records:
        print("No new/valid daily readings to push.")
        return 0
    url = f"{server.rstrip('/')}/api/docs/{doc_id}/tables/{table_id}/records"
    resp = requests.put(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"records": records},
        timeout=30,
    )
    if resp.status_code >= 300:
        print(f"Grist API error {resp.status_code}: {resp.text}", file=sys.stderr)
        resp.raise_for_status()
    print(f"Upserted {len(records)} daily reading(s) into Grist table {table_id!r}.")
    return len(records)
