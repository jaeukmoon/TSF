"""Weekly arXiv watcher: flag new LTSF papers that report on the classic
benchmark (ETT/Weather/ECL/Traffic ...) as candidates for the LTSF tab.

Detection only (0 model tokens). Candidates land in data/ltsf_pending.json;
the local Codex automation supervisor (`tsf-cards`) triages them, transcribes the tables
into data/ltsf.json, and clears the queue.
"""

import json
import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from common import http_get

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
WINDOW_DAYS = 9  # weekly cadence + slack

QUERY = ('(abs:"long-term time series forecasting" OR abs:"long-term forecasting" '
         'OR abs:"multivariate time series forecasting") AND (cat:cs.LG OR cat:stat.ML)')
API = ("http://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(QUERY)
       + "&sortBy=submittedDate&sortOrder=descending&max_results=100")

BENCH_PAT = re.compile(r"\bETTh?m?\d|\bETT\b", re.IGNORECASE)


def _load(name, default):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(name, obj):
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def run():
    seen = _load("ltsf_seen.json", {})
    pending = _load("ltsf_pending.json", [])
    cutoff = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)

    try:
        root = ET.fromstring(http_get(API).decode("utf-8"))
    except Exception as e:  # noqa: BLE001 - watcher must not fail the weekly run
        print(f"[ltsf-watch] arxiv query failed: {e}")
        return
    ns = {"a": "http://www.w3.org/2005/Atom"}

    added = 0
    pending_ids = {p["arxiv"] for p in pending}
    for entry in root.findall("a:entry", ns):
        arxiv_id = entry.findtext("a:id", "", ns).rsplit("/", 1)[-1].split("v")[0]
        published = entry.findtext("a:published", "", ns)
        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except ValueError:
            continue
        if pub_dt < cutoff:
            break  # sorted desc; everything after is older
        if arxiv_id in seen or arxiv_id in pending_ids:
            continue
        title = " ".join(entry.findtext("a:title", "", ns).split())
        abstract = " ".join(entry.findtext("a:summary", "", ns).split())
        if not BENCH_PAT.search(title + " " + abstract):
            continue
        pending.append({
            "arxiv": arxiv_id,
            "title": title,
            "published": published[:10],
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "abstract": abstract[:400],
        })
        seen[arxiv_id] = published[:10]
        added += 1

    _save("ltsf_pending.json", pending)
    _save("ltsf_seen.json", seen)
    print(f"[ltsf-watch] +{added} new candidates, {len(pending)} pending total")


if __name__ == "__main__":
    run()
