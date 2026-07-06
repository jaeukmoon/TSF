"""Shared helpers for the leaderboard tracker (stdlib only)."""

import json
import math
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "TSF-leaderboard-tracker (github.com/jaeukmoon/TSF)"}


def http_get(url: str, retries: int = 3, timeout: int = 30) -> bytes:
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - retry any network error
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"GET failed after {retries} tries: {url}: {last_err}")


def http_get_json(url: str):
    return json.loads(http_get(url).decode("utf-8"))


def quote_path(path: str) -> str:
    return urllib.parse.quote(path, safe="/")


def fetch_many(items, fn, workers: int = 8):
    """Run fn(item) concurrently, return list aligned with items. Errors -> None."""
    def safe(item):
        try:
            return fn(item)
        except Exception as e:  # noqa: BLE001 - one bad model must not kill the run
            print(f"  [warn] {item}: {e}")
            return None

    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(safe, items))


def gmean(values):
    vals = [v for v in values if v is not None and v > 0]
    if not vals:
        return None
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def mean(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return sum(vals) / len(vals)
