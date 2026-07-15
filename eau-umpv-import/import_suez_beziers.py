#!/usr/bin/env python3
"""Import daily water consumption for the Béziers site (SUEZ / toutsurmoneau.fr)
into the "Releves_Journaliers" Grist table.

Column names match the existing REPORT__EAU.grist document convention
(Site / Nom_du_CPT as plain Choice values, not a separate reference table).

Meant to run unattended (e.g. from a scheduled GitHub Actions workflow). All
configuration comes from environment variables so no secret ever needs to be
written to disk:

Required:
  SUEZ_USERNAME     Login for www.toutsurmoneau.fr
  SUEZ_PASSWORD     Password for www.toutsurmoneau.fr
  GRIST_API_KEY     Grist personal API key
  GRIST_DOC_ID      Grist document id (from the doc URL)
  GRIST_TABLE_ID    Grist table id for the readings table (e.g. "Releves_Journaliers")

Optional:
  SUEZ_METER_ID      Water meter id, only needed if the account has more than
                      one meter (toutsurmoneau raises an error telling you so)
  SUEZ_PROVIDER_URL  Alternate provider base URL, for non-SUEZ-branded portals
                      built on the same platform
  GRIST_SERVER       Grist server base URL (default: https://grist.numerique.gouv.fr,
                      matching the org this document already lives on)
  LOOKBACK_DAYS       How many days back to (re-)fetch and upsert on each run,
                      to catch data SUEZ publishes late (default: 40)
  SITE_NAME           Value written to the "Site" column (default: "Beziers") -
                      must be added to that column's Choice list in Grist
  NOM_DU_CPT          Value written to the "Nom_du_CPT" column (default: "CPT1"),
                      matching the CPT1/CPT2/CPT3 convention already in use
"""
import asyncio
import datetime
import sys

import aiohttp
import toutsurmoneau

from common.grist_upsert import env, push_records

GRIST_SERVER_DEFAULT = "https://grist.numerique.gouv.fr"
LOOKBACK_DAYS_DEFAULT = 40
SITE_NAME_DEFAULT = "Beziers"
NOM_DU_CPT_DEFAULT = "CPT1"


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


def to_grist_records(measures: list, site_name: str, nom_du_cpt: str) -> list:
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
            "Nom_du_CPT": nom_du_cpt,
            "Site": site_name,
            "Source": "SUEZ",
            "Volume_L": round(volume_m3 * 1000) if volume_m3 is not None else None,
            "Index_m3": index_m3,
        }
        records.append({"require": {"Date": date_ts, "Nom_du_CPT": nom_du_cpt}, "fields": fields})
    return records


def main() -> None:
    username = env("SUEZ_USERNAME")
    password = env("SUEZ_PASSWORD")
    meter_id = env("SUEZ_METER_ID", required=False)
    provider_url = env("SUEZ_PROVIDER_URL", required=False)

    grist_api_key = env("GRIST_API_KEY")
    grist_doc_id = env("GRIST_DOC_ID")
    grist_table_id = env("GRIST_TABLE_ID")
    grist_server = env("GRIST_SERVER", required=False, default=GRIST_SERVER_DEFAULT)

    site_name = env("SITE_NAME", required=False, default=SITE_NAME_DEFAULT)
    nom_du_cpt = env("NOM_DU_CPT", required=False, default=NOM_DU_CPT_DEFAULT)
    lookback_days = int(env("LOOKBACK_DAYS", required=False, default=str(LOOKBACK_DAYS_DEFAULT)))

    today = datetime.date.today()
    date_begin = today - datetime.timedelta(days=lookback_days)

    measures = asyncio.run(fetch_measures(username, password, meter_id, provider_url, date_begin, today))
    records = to_grist_records(measures, site_name, nom_du_cpt)
    push_records(grist_server, grist_doc_id, grist_table_id, grist_api_key, records)


if __name__ == "__main__":
    main()
