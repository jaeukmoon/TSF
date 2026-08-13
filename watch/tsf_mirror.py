#!/usr/bin/env python3
"""TSF 트렌드 미러 (stdlib only).

public 레포 jaeukmoon/TSF 의 data/{leaderboard,ltsf}.json 을 pull 해
state/tsf_snapshot.json 으로 캐시하고, 직전 스냅샷과의 델타(신규 모델·순위 변동·
신규 논문행)를 state/tsf_deltas.json 에 누적한다. TSF 파이프라인(주간 GH Actions)은
그대로 두고 소비만 한다 — 파이프라인 중복 없음 (2-레이어 설계).

사용:  python tsf_mirror.py        # 네트워크 실패 시 로컬 클론(../../../TSF) 폴백
이후:  python ../build_site.py     # tsf.html 갱신
"""
import datetime as dt
import json
import os
import sys
import urllib.request

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
SNAP_PATH = os.path.join(STATE, "tsf_snapshot.json")
DELTAS_PATH = os.path.join(STATE, "tsf_deltas.json")

RAW_BASE = "https://raw.githubusercontent.com/jaeukmoon/TSF/main/data"
# 같은 머신에 TSF 클론이 있으면 오프라인 폴백 (Desktop/GitHub/TSF 레이아웃)
LOCAL_TSF = os.path.abspath(os.path.join(HERE, "..", "..", "..", "TSF", "data"))
FILES = ["leaderboard.json", "ltsf.json"]
DELTA_KEEP = 20
TOP_N_TRACK = 10  # 순위 변동 추적 범위


def _fetch(name):
    url = f"{RAW_BASE}/{name}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "XIF_RL_watch/0.1"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8")), "remote"
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[warn] remote fetch failed {url}: {e}\n")
    local = os.path.join(LOCAL_TSF, name)
    if os.path.exists(local):
        with open(local, encoding="utf-8") as f:
            return json.load(f), "local"
    return None, "unavailable"


def _names(rows, key="name"):
    return [r.get(key, "") for r in rows or []]


def compute_delta(prev, cur):
    """직전 스냅샷 대비 변화 요약. prev 가 없으면 None."""
    if not prev:
        return None
    d = {"at": cur["fetched_at"], "changes": []}

    def diff_list(label, old_rows, new_rows):
        old_names, new_names = set(_names(old_rows)), set(_names(new_rows))
        for n in sorted(new_names - old_names):
            d["changes"].append(f"[{label}] 신규: {n}")
        # top-N 순위 변동
        old_top = _names(old_rows)[:TOP_N_TRACK]
        new_top = _names(new_rows)[:TOP_N_TRACK]
        for i, n in enumerate(new_top):
            if n in old_top and old_top.index(n) != i:
                d["changes"].append(f"[{label}] 순위: {n} {old_top.index(n)+1}→{i+1}위")
            elif n not in old_top:
                d["changes"].append(f"[{label}] top{TOP_N_TRACK} 진입: {n} ({i+1}위)")

    lb_old, lb_new = prev.get("leaderboard") or {}, cur.get("leaderboard") or {}
    # gift 는 rank_crps 오름차순이 순위 (TSF 사이트 집계와 동일)
    gift_old = sorted(lb_old.get("gift", []), key=lambda r: r.get("rank_crps", 1e9))
    gift_new = sorted(lb_new.get("gift", []), key=lambda r: r.get("rank_crps", 1e9))
    diff_list("GIFT-Eval", gift_old, gift_new)
    fev_old = sorted(lb_old.get("fev", []), key=lambda r: -(r.get("win_rate") or 0))
    fev_new = sorted(lb_new.get("fev", []), key=lambda r: -(r.get("win_rate") or 0))
    diff_list("fev-bench", fev_old, fev_new)

    lt_old, lt_new = prev.get("ltsf") or {}, cur.get("ltsf") or {}
    old_m = {m.get("name") for m in lt_old.get("models", [])}
    for m in lt_new.get("models", []):
        if m.get("name") not in old_m:
            src = (m.get("source") or {})
            d["changes"].append(
                f"[LTSF 논문] 신규: {m.get('name')} ({src.get('venue') or src.get('arxiv') or '?'})"
                + (" · ILI 포함" if "ILI" in (m.get("results") or {}) else ""))
    return d if d["changes"] else None


def main():
    os.makedirs(STATE, exist_ok=True)
    lb, lb_src = _fetch("leaderboard.json")
    lt, lt_src = _fetch("ltsf.json")
    if lb is None and lt is None:
        print("[tsf_mirror] 원격/로컬 모두 실패 — 기존 스냅샷 유지")
        sys.exit(1)

    prev = None
    if os.path.exists(SNAP_PATH):
        try:
            with open(SNAP_PATH, encoding="utf-8") as f:
                prev = json.load(f)
        except json.JSONDecodeError:
            prev = None

    cur = {
        "fetched_at": dt.datetime.now(dt.timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M"),
        "source": {"leaderboard": lb_src, "ltsf": lt_src},
        "leaderboard": lb if lb is not None else (prev or {}).get("leaderboard"),
        "ltsf": lt if lt is not None else (prev or {}).get("ltsf"),
    }
    delta = compute_delta(prev, cur)

    with open(SNAP_PATH, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=1)

    deltas = []
    if os.path.exists(DELTAS_PATH):
        try:
            with open(DELTAS_PATH, encoding="utf-8") as f:
                deltas = json.load(f).get("deltas", [])
        except json.JSONDecodeError:
            pass
    if delta:
        deltas = [delta] + deltas
    deltas = deltas[:DELTA_KEEP]
    with open(DELTAS_PATH, "w", encoding="utf-8") as f:
        json.dump({"deltas": deltas}, f, ensure_ascii=False, indent=1)

    n_gift = len((cur.get("leaderboard") or {}).get("gift", []))
    n_fev = len((cur.get("leaderboard") or {}).get("fev", []))
    n_lt = len((cur.get("ltsf") or {}).get("models", []))
    print(f"[tsf_mirror] snapshot ok (lb={lb_src} ltsf={lt_src}) "
          f"gift={n_gift} fev={n_fev} ltsf_models={n_lt} "
          f"delta={'+' + str(len(delta['changes'])) + '건' if delta else '없음'}")


if __name__ == "__main__":
    main()
