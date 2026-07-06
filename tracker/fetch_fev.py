"""Fetch fev-bench results (autogluon/fev GitHub repo) and aggregate them with
the official fev.analysis.leaderboard() methodology:
  - errors matrix task x model of test_error, relative to seasonal_naive
  - clip relative errors to [1e-2, 100], impute missing with 1.0
  - win_rate = mean pairwise wins (ties = 0.5), skill_score = 1 - gmean(rel err)
"""

import csv
import io

from common import fetch_many, gmean, http_get, http_get_json

RESULTS_API = "https://api.github.com/repos/autogluon/fev/contents/benchmarks/fev_bench/results"
BASELINE = "Seasonal naive"
MIN_REL, MAX_REL = 1e-2, 100.0


def list_csvs() -> list[str]:
    files = http_get_json(RESULTS_API)
    return [f["download_url"] for f in files if f["name"].endswith(".csv")]


def fetch_csv(url: str) -> list[dict]:
    text = http_get(url).decode("utf-8")
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            err = float(row["test_error"])
        except (KeyError, ValueError):
            err = None
        rows.append({
            "model": row["model_name"],
            "task": row["task_name"],
            "error": err,
            "inference_time_s": _to_float(row.get("inference_time_s")),
            "trained_on": row.get("trained_on_this_dataset", "").strip().lower() == "true",
        })
    return rows


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def aggregate(rows: list[dict]) -> list[dict]:
    models = sorted({r["model"] for r in rows})
    tasks = sorted({r["task"] for r in rows})
    cell = {(r["task"], r["model"]): r for r in rows}

    norm = lambda s: s.lower().replace(" ", "").replace("_", "").replace("-", "")
    baseline = next((m for m in models if norm(m) == norm(BASELINE)), None)
    if baseline is None:
        raise RuntimeError(f"baseline '{BASELINE}' missing; models: {models}")

    base_err = {}
    for t in tasks:
        b = cell.get((t, baseline))
        if b and b["error"] and b["error"] > 0:
            base_err[t] = b["error"]
    tasks = [t for t in tasks if t in base_err]

    # relative errors, clipped; missing imputed with 1.0 (= baseline)
    rel = {}
    failures = {m: 0 for m in models}
    for m in models:
        for t in tasks:
            r = cell.get((t, m))
            if r is None or r["error"] is None:
                failures[m] += 1
                rel[(t, m)] = 1.0
            else:
                rel[(t, m)] = min(max(r["error"] / base_err[t], MIN_REL), MAX_REL)

    entries = []
    for m in models:
        wins = 0.0
        for opp in models:
            if opp == m:
                continue
            for t in tasks:
                a, b = rel[(t, m)], rel[(t, opp)]
                wins += 1.0 if a < b else (0.5 if a == b else 0.0)
        n_cmp = len(tasks) * (len(models) - 1)
        inf_times = sorted(
            v for t in tasks
            if (c := cell.get((t, m))) and (v := c["inference_time_s"]) is not None
        )
        overlap = sum(
            1 for t in tasks if (c := cell.get((t, m))) and c["trained_on"]
        ) / len(tasks)
        entries.append({
            "name": m,
            "win_rate": wins / n_cmp if n_cmp else None,
            "skill_score": 1 - gmean(rel[(t, m)] for t in tasks),
            "median_inference_time_s": inf_times[len(inf_times) // 2] if inf_times else None,
            "overlap": overlap,
            "num_failures": failures[m],
            "n_tasks": len(tasks),
        })
    entries.sort(key=lambda e: -(e["win_rate"] or 0))
    return entries


def fetch() -> list[dict]:
    urls = list_csvs()
    print(f"[fev] {len(urls)} result files listed")
    all_rows = []
    for rows in fetch_many(urls, fetch_csv):
        if rows:
            all_rows.extend(rows)
    print(f"[fev] {len(all_rows)} task rows fetched")
    return aggregate(all_rows)


if __name__ == "__main__":
    import json

    entries = fetch()
    print(json.dumps(entries[:5], indent=2, ensure_ascii=False))
