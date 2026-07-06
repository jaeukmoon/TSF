"""Daily leaderboard tracker orchestrator.

fetch GIFT-Eval + fev-bench -> aggregate -> diff against the seen ledger ->
generate Sonnet summary cards for new/pending models -> write site data JSON.

Run from repo root or tracker/:  python tracker/update.py
Env: ANTHROPIC_API_KEY (optional; without it new cards stay pending)
     MAX_CARDS (default 12) - cards generated per run
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

MAX_CARDS = int(os.environ.get("MAX_CARDS", "12"))


def load(name, default):
    try:
        with open(os.path.join(DATA, name), encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save(name, obj):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def norm_key(name):
    """Merge identity across sources: 'Chronos-2' and 'chronos-2' -> 'chronos2'."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    gift = fetch_gift.fetch()
    fev = fetch_fev.fetch()

    seen = load("seen.json", {"gift": {}, "fev": {}})
    cards = load("cards.json", {})

    # mark first_seen per source
    new_names = []
    for source, entries in (("gift", gift), ("fev", fev)):
        for e in entries:
            if e["name"] not in seen[source]:
                seen[source][e["name"]] = today
                new_names.append((source, e["name"]))
    if new_names:
        print(f"[new] {len(new_names)} new models: {[n for _, n in new_names]}")

    # ensure a card slot exists for every model, merged across sources
    gift_by_key = {norm_key(e["name"]): e for e in gift}
    fev_by_key = {norm_key(e["name"]): e for e in fev}
    for source, entries in (("gift", gift), ("fev", fev)):
        for e in entries:
            key = norm_key(e["name"])
            slot = cards.setdefault(key, {
                "name": e["name"],
                "sources": {},
                "first_seen": seen[source][e["name"]],
                "status": "pending",
                "card": None,
            })
            slot["sources"][source] = e["name"]
            slot["first_seen"] = min(slot["first_seen"], seen[source][e["name"]])

    # generate cards for pending models (bounded per run)
    budget = MAX_CARDS
    for key, slot in sorted(cards.items(), key=lambda kv: kv[1]["first_seen"], reverse=True):
        if slot["status"] == "ok" or budget <= 0:
            continue
        g, f = gift_by_key.get(key), fev_by_key.get(key)
        info = {
            "org": (g or {}).get("org", ""),
            "model_type": (g or {}).get("model_type", ""),
            "model_link": (g or {}).get("model_link", ""),
            "code_link": (g or {}).get("code_link", ""),
            "testdata_leakage": (g or {}).get("leak", ""),
            "stats": {
                "gift_eval": g and {k: g[k] for k in
                                    ("mase", "crps", "rank_crps", "rank_mase", "n_configs")},
                "fev_bench": f and {k: f[k] for k in
                                    ("win_rate", "skill_score", "median_inference_time_s",
                                     "overlap", "num_failures")},
            },
        }
        print(f"[card] generating: {slot['name']}")
        card = summarize.make_card(slot["name"], info)
        if card is None:
            continue
        slot["card"] = card
        slot["status"] = "ok"
        slot["generated_at"] = today
        budget -= 1
        save("cards.json", cards)  # checkpoint so a crash keeps finished cards

    pending = sum(1 for s in cards.values() if s["status"] != "ok")
    print(f"[cards] {len(cards) - pending} ok, {pending} pending")

    save("seen.json", seen)
    save("cards.json", cards)
    save("leaderboard.json", {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "gift": gift,
        "fev": fev,
        "first_seen": seen,
    })
    print("[done] data/ updated")


if __name__ == "__main__":
    main()
