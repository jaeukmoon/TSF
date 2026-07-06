"""Fetch GIFT-Eval leaderboard results from the HF space and aggregate them
with the official methodology (src/utils.py of the space):
  - per (dataset/freq/term) config, normalize MASE[0.5] and CRPS by seasonal_naive
  - rank models per config by CRPS and by MASE
  - overall = geometric mean of normalized metrics + mean rank across configs
"""

import csv
import io

from common import fetch_many, gmean, http_get, http_get_json, mean, quote_path

SPACE = "Salesforce/GIFT-Eval"
TREE_URL = f"https://huggingface.co/api/spaces/{SPACE}/tree/main/results"
RAW_URL = f"https://huggingface.co/spaces/{SPACE}/raw/main/"

BASELINE = "seasonal_naive"
MASE_COL = "eval_metrics/MASE[0.5]"
CRPS_COL = "eval_metrics/mean_weighted_sum_quantile_loss"


def list_models() -> list[str]:
    tree = http_get_json(TREE_URL)
    return [f["path"].split("/", 1)[1] for f in tree if f["type"] == "directory"]


def fetch_model(name: str) -> dict:
    base = RAW_URL + quote_path(f"results/{name}")
    config = http_get_json(base + "/config.json")
    text = http_get(base + "/all_results.csv").decode("utf-8")
    rows = {}
    for row in csv.DictReader(io.StringIO(text)):
        try:
            rows[row["dataset"]] = {
                "mase": float(row[MASE_COL]),
                "crps": float(row[CRPS_COL]),
            }
        except (KeyError, ValueError):
            continue
    return {"name": name, "config": config, "rows": rows}


def _rank_per_config(models: list[dict], metric: str) -> dict[str, dict[str, int]]:
    """config_key -> {model_name: rank} (1-based, ascending metric, ties by order)."""
    all_keys = set()
    for m in models:
        all_keys.update(m["rows"].keys())
    ranks: dict[str, dict[str, int]] = {}
    for key in all_keys:
        scored = [(m["rows"][key][metric], m["name"]) for m in models if key in m["rows"]]
        scored.sort(key=lambda t: t[0])
        ranks[key] = {name: i + 1 for i, (_, name) in enumerate(scored)}
    return ranks


def aggregate(models: list[dict]) -> list[dict]:
    baseline = next((m for m in models if m["name"] == BASELINE), None)
    if baseline is None:
        raise RuntimeError(f"baseline '{BASELINE}' missing from GIFT-Eval results")

    rank_crps = _rank_per_config(models, "crps")
    rank_mase = _rank_per_config(models, "mase")

    entries = []
    for m in models:
        norm_mase, norm_crps, r_crps, r_mase = [], [], [], []
        for key, vals in m["rows"].items():
            base = baseline["rows"].get(key)
            if base and base["mase"] > 0 and base["crps"] > 0:
                norm_mase.append(vals["mase"] / base["mase"])
                norm_crps.append(vals["crps"] / base["crps"])
            r_crps.append(rank_crps[key][m["name"]])
            r_mase.append(rank_mase[key][m["name"]])
        cfg = m["config"]
        entries.append({
            "name": m["name"],
            "org": cfg.get("org") or "",
            "model_type": cfg.get("model_type") or "",
            "model_link": cfg.get("model_link") or "",
            "code_link": cfg.get("code_link") or "",
            "leak": cfg.get("testdata_leakage") or "",
            "mase": gmean(norm_mase),
            "crps": gmean(norm_crps),
            "rank_crps": mean(r_crps),
            "rank_mase": mean(r_mase),
            "n_configs": len(m["rows"]),
        })
    entries.sort(key=lambda e: e["crps"] if e["crps"] is not None else 1e9)
    return entries


def fetch() -> list[dict]:
    names = list_models()
    print(f"[gift] {len(names)} models listed")
    models = [m for m in fetch_many(names, fetch_model) if m]
    print(f"[gift] {len(models)} models fetched")
    return aggregate(models)


if __name__ == "__main__":
    import json

    entries = fetch()
    print(json.dumps(entries[:5], indent=2, ensure_ascii=False))
