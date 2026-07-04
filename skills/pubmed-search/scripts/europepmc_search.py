#!/usr/bin/env python3
"""Search Europe PMC and export structured records.

Usage:
    python europepmc_search.py --query '("bisphenol A") AND ("adipogenesis")' --email you@inst.edu --max 200 --out results/search

No API key required. Outputs <out>_records.csv and <out>_query.txt.
"""
import argparse
import csv
import os
import sys
import time
from datetime import datetime, timezone

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests pandas")

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search(query, email, source="MED", from_year=None, open_access_only=False, max_records=200):
    q = query
    if from_year:
        q = f"({q}) AND (PUB_YEAR:[{from_year} TO 3000])"
    if open_access_only:
        q = f"({q}) AND (OPEN_ACCESS:y)"
    if source:
        q = f"({q}) AND (SRC:{source})"

    records, cursor, fetched = [], "*", 0
    session = requests.Session()
    session.headers.update({"User-Agent": f"claud-minions-litscout ({email})"})

    while fetched < max_records:
        page_size = min(100, max_records - fetched)
        params = {
            "query": q,
            "format": "json",
            "resultType": "core",
            "pageSize": page_size,
            "cursorMark": cursor,
            "email": email,
        }
        r = session.get(BASE, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        results = data.get("resultList", {}).get("result", [])
        if not results:
            break
        for it in results:
            authors = it.get("authorString", "")
            records.append({
                "pmid": it.get("pmid", ""),
                "pmcid": it.get("pmcid", ""),
                "doi": it.get("doi", ""),
                "title": (it.get("title", "") or "").strip(),
                "authors": authors,
                "journal": it.get("journalInfo", {}).get("journal", {}).get("title", "")
                           or it.get("bookOrReportDetails", {}).get("publisher", ""),
                "year": it.get("pubYear", ""),
                "is_open_access": it.get("isOpenAccess", ""),
                "abstract": (it.get("abstractText", "") or "").strip(),
                "source": it.get("source", ""),
            })
        fetched += len(results)
        next_cursor = data.get("nextCursorMark")
        if not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.34)  # be polite to the API

    return q, records


def dedup(records):
    seen, out = set(), []
    for r in records:
        key = r["doi"].lower() or r["pmid"] or r["title"].lower()
        if key and key not in seen:
            seen.add(key)
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser(description="Search Europe PMC.")
    ap.add_argument("--query", required=True)
    ap.add_argument("--email", required=True, help="Contact email (API etiquette).")
    ap.add_argument("--source", default="MED", help="MED=PubMed, PMC=full text, PPR=preprints.")
    ap.add_argument("--from-year", type=int, default=None)
    ap.add_argument("--open-access-only", action="store_true")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--out", default="search")
    args = ap.parse_args()

    final_query, records = search(
        args.query, args.email, source=args.source, from_year=args.from_year,
        open_access_only=args.open_access_only, max_records=args.max,
    )
    n_raw = len(records)
    records = dedup(records)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    csv_path = f"{args.out}_records.csv"
    q_path = f"{args.out}_query.txt"

    fields = ["pmid", "pmcid", "doi", "title", "authors", "journal", "year",
              "is_open_access", "abstract", "source"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(q_path, "w", encoding="utf-8") as f:
        f.write(f"Europe PMC search\nTimestamp: {ts}\n")
        f.write(f"Executed query: {final_query}\n")
        f.write(f"Records found (raw): {n_raw}\n")
        f.write(f"Records after dedup: {len(records)}\n")

    print(f"Found {n_raw} records, {len(records)} after dedup.")
    print(f"Saved records -> {csv_path}")
    print(f"Saved query   -> {q_path}")


if __name__ == "__main__":
    main()
