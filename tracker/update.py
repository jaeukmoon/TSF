"""Deterministic leaderboard ingestion orchestrator.

Fetch GIFT-Eval and fev-bench, update the seen ledger, create facts-only cards
for undocumented submissions, and leave documented models pending for the
Codex `tsf-cards` project skill.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch_fev
import fetch_gift
import summarize
import watch_ltsf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(name, default):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name, value):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=1)
        file.write("\n")


def norm_key(name):
    """Merge identity across sources: `Chronos-2` and `chronos-2`."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    gift = fetch_gift.fetch()
    fev = fetch_fev.fetch()
    watch_ltsf.run()

    seen = load("seen.json", {"gift": {}, "fev": {}})
    cards = load("cards.json", {})

    new_names = []
    for source, entries in (("gift", gift), ("fev", fev)):
        for entry in entries:
            if entry["name"] not in seen[source]:
                seen[source][entry["name"]] = today
                new_names.append((source, entry["name"]))
    if new_names:
        print(f"[new] {len(new_names)} new models: {[name for _, name in new_names]}")

    gift_by_key = {norm_key(entry["name"]): entry for entry in gift}
    fev_by_key = {norm_key(entry["name"]): entry for entry in fev}
    for source, entries in (("gift", gift), ("fev", fev)):
        for entry in entries:
            key = norm_key(entry["name"])
            slot = cards.setdefault(
                key,
                {
                    "name": entry["name"],
                    "sources": {},
                    "first_seen": seen[source][entry["name"]],
                    "status": "pending",
                    "card": None,
                },
            )
            slot["sources"][source] = entry["name"]
            slot["first_seen"] = min(slot["first_seen"], seen[source][entry["name"]])

    for key, slot in sorted(
        cards.items(), key=lambda item: item[1]["first_seen"], reverse=True
    ):
        if slot["status"] == "ok":
            continue
        gift_entry, fev_entry = gift_by_key.get(key), fev_by_key.get(key)
        info = {
            "org": (gift_entry or {}).get("org", ""),
            "model_type": (gift_entry or {}).get("model_type", ""),
            "model_link": (gift_entry or {}).get("model_link", ""),
            "code_link": (gift_entry or {}).get("code_link", ""),
            "testdata_leakage": (gift_entry or {}).get("leak", ""),
            "stats": {
                "gift_eval": gift_entry
                and {
                    field: gift_entry[field]
                    for field in ("mase", "crps", "rank_crps", "rank_mase", "n_configs")
                },
                "fev_bench": fev_entry
                and {
                    field: fev_entry[field]
                    for field in (
                        "win_rate",
                        "skill_score",
                        "median_inference_time_s",
                        "overlap",
                        "num_failures",
                    )
                },
            },
        }
        if summarize.has_evidence(info):
            continue
        slot["card"] = summarize.template_card(slot["name"], info)
        slot["status"] = "ok"
        slot["generated_at"] = today
        slot["generated_by"] = "deterministic-template"

    pending = sum(1 for slot in cards.values() if slot["status"] != "ok")
    print(f"[cards] {len(cards) - pending} complete, {pending} pending for Codex")

    save("seen.json", seen)
    save("cards.json", cards)
    save(
        "leaderboard.json",
        {
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "gift": gift,
            "fev": fev,
            "first_seen": seen,
        },
    )
    print("[done] deterministic data updated")


if __name__ == "__main__":
    main()
