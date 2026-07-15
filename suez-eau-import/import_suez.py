#!/usr/bin/env python3
"""Import daily water consumption from toutsurmoneau.fr (SUEZ) into a Grist table.

Meant to run unattended (e.g. from a scheduled GitHub Actions workflow). All
configuration comes from environment variables so no secret ever needs to be
written to disk:

Required:
  SUEZ_USERNAME     Login for www.toutsurmoneau.fr
  SUEZ_PASSWORD     Password for www.toutsurmoneau.fr
  GRIST_API_KEY     Grist personal API key
  GRIST_DOC_ID      Grist document id (from the doc URL)
  GRIST_TABLE_ID    Grist table id (the machine name, e.g. "Consommation_eau")

Optional:
  SUEZ_METER_ID     Water meter id, only needed if the account has more than
                     one meter (toutsurmoneau raises an error telling you so)
  SUEZ_PROVIDER_URL Alternate provider base URL, for non-SUEZ-branded portals
                     built on the same platform
  GRIST_SERVER      Grist server base URL (default: https://docs.getgrist.com)
  LOOKBACK_DAYS      How many days back to (re-)fetch and upsert on each run,
                     to catch data SUEZ publishes late (default: 40)
"""
import asyncio
import datetime
import os
import sys

import aiohttp
import requests
import toutsurmoneau

GRIST_SERVER_DEFAULT = "https://docs.getgrist.com"
LOOKBACK_DAYS_DEFAULT = 40


def env(name: str, required: bool = True, default: str = None) -> str:
    # GitHub Actions sets env vars for unset secrets to "" rather than leaving
    # them unset, so treat blank the same as missing before applying default.
    value = os.environ.get(name) or default
    if required and not value:
        print(f"Missing required environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


async def fetch_measures(username: str, password: str, meter_id: str, provider_url: str,
                          date_begin: datetime.date, date_end: datetime.date) -> list:
    async with aiohttp.ClientSession() as session:
        client = toutsurmoneau.AsyncClient(
            username=username,
            password=password,
            meter_id=meter_id,
            url=provider_url,
            session=session,
            use_litre=False,
        )
        if not await client.async_check_credentials():
            print("SUEZ login failed: check SUEZ_USERNAME / SUEZ_PASSWORD.", file=sys.stderr)
            sys.exit(1)
        return await client.async_telemetry(mode="daily", date_begin=date_begin, date_end=date_end)


def to_grist_records(measures: list) -> list:
    records = []
    for m in measures:
        index_m3 = m.get("index")
        volume_m3 = m.get("volume")
        if index_m3 is None or int(index_m3) == 0:
            # No reading published yet for that day (SUEZ zero-fills the future).
            continue
        day = datetime.datetime.strptime(m["date"].split(" ")[0], "%Y-%m-%d").date()
        date_ts = int(datetime.datetime(day.year, day.month, day.day,
                                         tzinfo=datetime.timezone.utc).timestamp())
        fields = {
            "Date": date_ts,
            "Volume_L": round(volume_m3 * 1000) if volume_m3 is not None else None,
            "Index_m3": index_m3,
        }
        records.append({"require": {"Date": date_ts}, "fields": fields})
    return records


def push_to_grist(server: str, doc_id: str, table_id: str, api_key: str, records: list) -> None:
    if not records:
        print("No new/valid daily readings to push.")
        return
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


def main() -> None:
    username = env("SUEZ_USERNAME")
    password = env("SUEZ_PASSWORD")
    meter_id = env("SUEZ_METER_ID", required=False)
    provider_url = env("SUEZ_PROVIDER_URL", required=False)

    grist_api_key = env("GRIST_API_KEY")
    grist_doc_id = env("GRIST_DOC_ID")
    grist_table_id = env("GRIST_TABLE_ID")
    grist_server = env("GRIST_SERVER", required=False, default=GRIST_SERVER_DEFAULT)

    lookback_days = int(env("LOOKBACK_DAYS", required=False, default=str(LOOKBACK_DAYS_DEFAULT)))

    today = datetime.date.today()
    date_begin = today - datetime.timedelta(days=lookback_days)

    measures = asyncio.run(fetch_measures(username, password, meter_id, provider_url, date_begin, today))
    records = to_grist_records(measures)
    push_to_grist(grist_server, grist_doc_id, grist_table_id, grist_api_key, records)


if __name__ == "__main__":
    main()
