#!/usr/bin/env python3
"""XIF-RL RL-Watch — 결정적 논문 수집기 (stdlib only, LLM 없음).

WM/surveybot/fetch_papers.py 이식(provenance). arXiv API + HuggingFace Papers 에서
최근 논문을 모아 정규화 → 3 게이트 필터 → dedup(seen.json) → 자동 ingest:

  Gate A rl_tsf   : 시계열 구절 AND RL 구절 동시 매치 (교집합 희귀 → 무게이트)
  Gate B algo     : 제목에 RL 핵심구/알고리즘명 + LLM 문맥 + (탑학회|빅테크|HF) 게이트
  Gate C baseline : Time-R1/TimeMaster 를 인용·비교 (본문 HTML 스캔 포함) — 무조건 포함
         epi      : 인플루엔자/역학 예측 — 무조건 포함

WM 과 달리 triage 에이전트 없이 fetch 가 곧바로 state/papers.json 에 누적한다
(카드 = 메타데이터 + abstract; 요약/딥다이브는 필요할 때 스킬로).

사용:
    python fetch_papers.py [--hours 168] [--max 3000] [--no-ingest] [--out PATH]
이후:
    python ../build_site.py   # watch.html 갱신
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402  (같은 폴더의 sources.py)

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "state")
SEEN_PATH = os.path.join(STATE, "seen.json")
PAPERS_PATH = os.path.join(STATE, "papers.json")
NOTIFY_PATH = os.path.join(STATE, "notify.json")
DEFAULT_OUT = os.path.join(STATE, "candidates.json")

UA = "XIF_RL_watch/0.1 (research paper survey; contact: local)"
ARXIV_API = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


# ----------------------------- helpers -----------------------------
def _get(url, timeout=30, tries=3):
    """GET with real UA + retry/backoff. Returns bytes or None."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == tries - 1:
                sys.stderr.write(f"[warn] GET failed ({attempt+1}/{tries}) {url}: {e}\n")
                return None
            time.sleep(3 * (attempt + 1))  # arXiv asks <=1 req/3s
    return None


def normalize_id(raw):
    """'http://arxiv.org/abs/2606.12345v2' -> ('2606.12345','v2')."""
    if not raw:
        return None, None
    tail = raw.rstrip("/").split("/")[-1]
    m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?$", tail)
    if m:
        return m.group(1), (m.group(2) or "")
    return tail, ""


def _any_sub(text_lc, phrases):
    return [p for p in phrases if p in text_lc]


def _any_acr(text_raw, acronyms):
    return [a for a in acronyms if re.search(rf"\b{re.escape(a)}\b", text_raw)]


def classify(title, abstract, comment, hf_upvotes, top_conf, bigtech, from_hf):
    """3 게이트 분류. -> (watch_type or None, matched list).
    우선순위: epi > rl_tsf > algo (baseline 은 호출부에서 별도 강제)."""
    text_lc = f"{title} {abstract}".lower()
    text_raw = f"{title} {abstract}"
    title_lc = title.lower()

    # Gate C-2: 역학/ILI — 무조건 포함
    epi = _any_sub(text_lc, sources.EPI_PHRASES) + _any_acr(text_raw, sources.EPI_ACRONYMS)
    if epi:
        return "epi", epi

    ts_hits = _any_sub(text_lc, sources.TS_PHRASES)
    rl_hits = _any_sub(text_lc, sources.RL_PHRASES) + _any_acr(text_raw, sources.RL_ACRONYMS)

    # Gate A: RL × 시계열
    if ts_hits and rl_hits:
        return "rl_tsf", ts_hits + rl_hits

    # Gate B: RL 알고리즘 트렌드
    name_hits = _any_acr(title, sources.ALGO_NAME_ACRONYMS)
    title_hits = _any_sub(title_lc, sources.ALGO_TITLE_PHRASES)
    signal = (top_conf or bigtech or from_hf
              or (hf_upvotes or 0) >= sources.HF_UPVOTE_MIN)
    if name_hits or title_hits:
        anchors = _any_sub(text_lc, sources.LLM_ANCHORS)
        if anchors:
            if name_hits:  # 알고리즘명 제목 매치 = 게이트 면제
                return "algo", name_hits + anchors
            if signal:
                return "algo", title_hits + anchors

    # Gate D: 예측 트렌드 (RL 무관) — 제목 예측구 + (강제구|모델명|신호 게이트)
    ts_title = _any_sub(title_lc, sources.TSF_TITLE_PHRASES)
    if ts_title and "forecast" not in title_lc and _any_sub(title_lc, sources.TSF_NEG_TITLE):
        ts_title = []  # 비예측 태스크(anomaly/classification 등) 컷
    if ts_title:
        hot = _any_sub(text_lc, sources.TSF_HOT_PHRASES)
        model_toks = _any_sub(title_lc, sources.TSF_MODEL_TOKENS)
        if hot or model_toks:  # 확률예측/보정·파운데이션 모델명 = 게이트 면제
            return "tsf_trend", ts_title + hot + model_toks
        if top_conf:  # 일반 예측 논문은 탑학회 게재만 (완성도 프록시)
            return "tsf_trend", ts_title
    return None, []


def detect_bigtech(title, abstract, authors):
    blob = f"{title} {abstract} {' '.join(authors or [])}".lower()
    author_blob = " ".join(authors or []).lower()
    title_lc = title.lower()
    orgs, reasons = [], []
    for org, info in sources.BIGTECH_ORGS.items():
        target = author_blob if info.get("affil_strict") else blob
        if any(sub in target for sub in info.get("affil", [])):
            orgs.append(org)
            reasons.append(f"affil:{org}")
    for tok in sources.BIGTECH_TITLE_TOKENS:
        if tok in title_lc:
            reasons.append(f"title_token:{tok}")
    bigtech = bool(orgs) or any(r.startswith("title_token") for r in reasons)
    return bigtech, sorted(set(orgs)), reasons


def detect_tracked_baselines(*texts):
    blob = " ".join(t for t in texts if t)
    return [name for name, pat in sources.TRACKED_BASELINES.items()
            if re.search(rf"\b{pat}\b", blob, re.IGNORECASE)]


def detect_topconf(comment):
    c = (comment or "").lower()
    for v in sources.TOP_CONF:
        if re.search(rf"\b{re.escape(v)}\b", c):
            return v.upper()
    return ""


HTML_SCAN_CAP = 40  # run당 arxiv HTML fetch 상한 (rate-limit 보호)
_html_scans = [0]
_html_cache = {}


def scan_html_baselines(aid):
    """arXiv HTML 본문에서 Time-R1/TimeMaster 언급 탐지 — 비교표는 보통 abstract 밖."""
    if aid in _html_cache:
        html = _html_cache[aid]
    elif _html_scans[0] >= HTML_SCAN_CAP:
        return []
    else:
        _html_scans[0] += 1
        raw = _get(f"https://arxiv.org/html/{aid}", timeout=20, tries=2)
        time.sleep(1.0)
        html = raw.decode("utf-8", "replace") if raw is not None else None
        _html_cache[aid] = html
    if html is None:
        return []
    text = re.sub(r"<[^>]+>", " ", html)
    return detect_tracked_baselines(text)


# ----------------------------- arXiv (페이지네이션) -----------------------------
def fetch_arxiv(hours, max_total, page_size=500):
    """주간(168h) 윈도우는 4개 카테고리에서 1000건을 훌쩍 넘어 recency 윈도우 밖으로
    밀린다(WM 의 2026-06-12 실측과 동일 계열 문제) → start 오프셋 페이지네이션."""
    cat_q = " OR ".join(f"cat:{c}" for c in sources.ARXIV_CATEGORIES)
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    out, start, status = [], 0, "ok"
    while start < max_total:
        params = {
            "search_query": cat_q, "sortBy": "submittedDate", "sortOrder": "descending",
            "start": start, "max_results": min(page_size, max_total - start),
        }
        raw = _get(ARXIV_API + "?" + urllib.parse.urlencode(params, safe=":+"))
        if raw is None:
            status = "error" if not out else "partial"
            break
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(raw)
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] arxiv parse failed @start={start}: {e}\n")
            status = "error" if not out else "partial"
            break
        entries = root.findall(f"{ATOM}entry")
        if not entries:
            break
        oldest_in_page = None
        for entry in entries:
            raw_id = entry.findtext(f"{ATOM}id", default="")
            aid, ver = normalize_id(raw_id)
            title = " ".join((entry.findtext(f"{ATOM}title") or "").split())
            abstract = " ".join((entry.findtext(f"{ATOM}summary") or "").split())
            published = entry.findtext(f"{ATOM}published", default="")
            try:
                pub_dt = dt.datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                pub_dt = None
            if pub_dt is not None:
                oldest_in_page = pub_dt
                if pub_dt < cutoff:
                    continue
            authors = [a.findtext(f"{ATOM}name") or "" for a in entry.findall(f"{ATOM}author")]
            comment = entry.findtext(f"{ARXIV_NS}comment", default="") or ""
            out.append({
                "id": aid, "version": ver, "title": title, "abstract": abstract,
                "authors": authors, "comment": comment,
                "url": f"https://arxiv.org/abs/{aid}", "pdf": f"https://arxiv.org/pdf/{aid}",
                "published": published, "source": ["arxiv"], "hf_upvotes": None,
            })
        if oldest_in_page is not None and oldest_in_page < cutoff:
            break  # 윈도우 끝까지 내려왔음
        start += len(entries)
        time.sleep(3.0)  # arXiv 예의
    return out, status


# ----------------------------- HuggingFace Papers -----------------------------
def _hf_one_day(date_str):
    raw = _get(f"https://huggingface.co/papers?date={date_str}")
    items = []
    if raw is not None:
        html = raw.decode("utf-8", "replace")
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                for it in _walk_daily(data):
                    p = it.get("paper", it) or {}
                    pid = p.get("id") or it.get("id")
                    if not pid:
                        continue
                    authors = []
                    for a in (p.get("authors") or []):
                        nm = a.get("name") if isinstance(a, dict) else a
                        if nm:
                            authors.append(nm)
                    items.append({
                        "id": pid, "title": (p.get("title") or "").strip(),
                        "abstract": (p.get("summary") or "").strip(),
                        "authors": authors, "upvotes": p.get("upvotes") or it.get("upvotes"),
                    })
            except Exception as e:  # noqa: BLE001
                sys.stderr.write(f"[warn] HF __NEXT_DATA__ parse failed: {e}\n")
    if items:
        return items, "ok"
    raw = _get(f"https://huggingface.co/api/daily_papers?date={date_str}")
    if raw is not None:
        try:
            data = json.loads(raw.decode("utf-8", "replace"))
            for it in (data if isinstance(data, list) else []):
                p = it.get("paper", it) or {}
                pid = p.get("id") or it.get("id")
                if not pid:
                    continue
                authors = [a.get("name") if isinstance(a, dict) else a for a in (p.get("authors") or [])]
                items.append({
                    "id": pid, "title": (p.get("title") or "").strip(),
                    "abstract": (p.get("summary") or "").strip(),
                    "authors": [a for a in authors if a], "upvotes": p.get("upvotes"),
                })
            if items:
                return items, "fallback"
        except Exception as e:  # noqa: BLE001
            sys.stderr.write(f"[warn] HF fallback parse failed: {e}\n")
    return [], "unavailable"


def _walk_daily(data):
    try:
        pp = data["props"]["pageProps"]
        for key in ("dailyPapers", "papers", "initialPapers"):
            if isinstance(pp.get(key), list):
                return pp[key]
    except Exception:  # noqa: BLE001
        pass
    found = []

    def rec(o):
        if found:
            return
        if isinstance(o, list):
            if o and isinstance(o[0], dict) and ("paper" in o[0] or "id" in o[0]):
                found.append(o)
                return
            for x in o:
                rec(x)
        elif isinstance(o, dict):
            for v in o.values():
                rec(v)

    rec(data)
    return found[0] if found else []


def fetch_hf(date_str, hours):
    base = dt.datetime.strptime(date_str, "%Y-%m-%d")
    days = min(7, 1 + max(0, (hours - 1) // 24))
    all_items, status = [], "unavailable"
    for k in range(days):
        d = (base - dt.timedelta(days=k)).strftime("%Y-%m-%d")
        items, st = _hf_one_day(d)
        if st != "unavailable" and status == "unavailable":
            status = st
        all_items.extend(items)
    return all_items, status


# ----------------------------- state -----------------------------
def _read_store(path, key):
    """누적 스토어 로드. 손상(JSONDecodeError) 시 .corrupt 로 보존하고 중단 —
    빈 리스트로 조용히 덮어쓰면 몇 주치 누적 카드가 비가역 소실되고, 온전한
    seen.json 이 재수집까지 막아 손실이 고착된다 (2026-07-12 검증 워크플로 실증)."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get(key, [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        bak = path + ".corrupt"
        os.replace(path, bak)
        sys.stderr.write(f"[fatal] {os.path.basename(path)} 손상({e}) — {bak} 로 보존. "
                         f"복구(또는 삭제 승인) 후 재실행.\n")
        raise SystemExit(2)


def _write_atomic(path, obj):
    """temp 쓰기 + os.replace — 쓰기 중단이 스토어를 반파하지 않도록."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def load_seen():
    seen = {normalize_id(x)[0] or x for x in _read_store(SEEN_PATH, "seen")}
    seen |= {normalize_id(p.get("id"))[0] or p.get("id")
             for p in _read_store(PAPERS_PATH, "papers") if p.get("id")}
    return seen


def ingest(candidates, run_date):
    """candidates → papers.json 앞쪽에 누적 + seen.json 갱신 (결정적, triage 없음)."""
    papers = _read_store(PAPERS_PATH, "papers")
    have = {p.get("id") for p in papers}
    fresh = [c for c in candidates if c["id"] not in have]
    for c in fresh:
        c["ingested"] = run_date
    papers = fresh + papers
    _write_atomic(PAPERS_PATH, {"papers": papers})

    seen_list = _read_store(SEEN_PATH, "seen")
    seen_set = set(seen_list)
    seen_list += [c["id"] for c in fresh if c["id"] not in seen_set]
    _write_atomic(SEEN_PATH, {"seen": seen_list})
    return len(fresh), len(papers)


# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser(description="RL×TSF / RL-algo weekly paper fetcher (arXiv + HF).")
    ap.add_argument("--hours", type=int, default=168)
    ap.add_argument("--max", type=int, default=3000, help="arXiv 페이지네이션 총 상한")
    ap.add_argument("--date", default=dt.datetime.utcnow().strftime("%Y-%m-%d"))
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--no-ingest", action="store_true", help="papers/seen 갱신 없이 candidates 만")
    args = ap.parse_args()

    seen = load_seen()
    arxiv_items, arxiv_status = fetch_arxiv(args.hours, args.max)
    hf_items, hf_status = fetch_hf(args.date, args.hours)
    fetched = len(arxiv_items) + len(hf_items)

    merged = {}
    for it in arxiv_items:
        merged[it["id"]] = it
    for h in hf_items:
        aid, ver = normalize_id(h["id"])
        key = aid or f"hf:{h['id']}"
        if key in merged:
            rec = merged[key]
            if "hf" not in rec["source"]:
                rec["source"].append("hf")
            rec["hf_upvotes"] = h.get("upvotes")
        else:
            merged[key] = {
                "id": aid or h["id"], "version": ver, "title": h["title"],
                "abstract": h["abstract"], "authors": h.get("authors", []),
                "comment": "", "url": f"https://arxiv.org/abs/{aid}" if aid else "",
                "pdf": f"https://arxiv.org/pdf/{aid}" if aid else "",
                "published": args.date, "source": ["hf"], "hf_upvotes": h.get("upvotes"),
            }

    candidates = []
    counts = {k: 0 for k in sources.WATCH_TYPES}
    for rec in merged.values():
        nid = normalize_id(rec["id"])[0] or rec["id"]
        if nid in seen:
            continue
        conf = detect_topconf(rec.get("comment", ""))
        bt, orgs, reasons = detect_bigtech(rec["title"], rec["abstract"], rec.get("authors"))
        wtype, matched = classify(
            rec["title"], rec["abstract"], rec.get("comment", ""),
            rec.get("hf_upvotes"), conf, bt, "hf" in rec["source"])
        # baseline watch: 제목/초록/comment 매치 → 아니면 게이트 통과 후보 전체에 본문 스캔
        # (rl_tsf/epi 로 좁히면 Time-R1/TimeMaster 를 본문 비교표에서 인용하는 tsf_trend
        #  후속 논문을 놓침 — 캡(HTML_SCAN_CAP)이 예산을 보호하므로 전 타입 스캔)
        bl = detect_tracked_baselines(rec["title"], rec["abstract"], rec.get("comment", ""))
        if not bl and wtype is not None and rec["id"] and not str(rec["id"]).startswith("hf:"):
            bl = scan_html_baselines(rec["id"])
        if bl:
            wtype = "baseline"
            matched = bl + matched
        if wtype is None:
            continue
        rec["watch_type"] = wtype
        rec["matched"] = sorted(set(matched))
        rec["baseline_watch"] = bl
        rec["top_conf"] = conf
        rec["bigtech"] = bt
        rec["bigtech_orgs"] = orgs
        counts[wtype] += 1
        candidates.append(rec)

    prio = {"baseline": 4, "epi": 3, "rl_tsf": 2, "algo": 1, "tsf_trend": 0}
    candidates.sort(key=lambda r: (prio[r["watch_type"]], r["bigtech"], bool(r["top_conf"]),
                                   r.get("hf_upvotes") or 0, r["id"]), reverse=True)

    out = {
        "run_date": args.date, "window_hours": args.hours,
        "arxiv_status": arxiv_status, "hf_status": hf_status,
        "counts": {"fetched": fetched, "after_filter": len(candidates),
                   "html_scans": _html_scans[0], **counts},
        "candidates": candidates,
    }
    os.makedirs(STATE, exist_ok=True)
    _write_atomic(args.out, out)

    # 알림 대상(강제 포함 히트)만 따로 — GH Actions telegram 단계가 소비
    hot = [{"id": c["id"], "title": c["title"], "watch_type": c["watch_type"],
            "matched": c["matched"], "url": c["url"]}
           for c in candidates if c["watch_type"] in ("baseline", "epi")]
    _write_atomic(NOTIFY_PATH, {"run_date": args.date, "hits": hot})

    if not args.no_ingest:
        n_fresh, n_total = ingest(candidates, args.date)
        print(f"[fetch] ingest: +{n_fresh} → papers.json {n_total}편")

    print(f"[fetch] arxiv={arxiv_status} hf={hf_status} | fetched={fetched} "
          f"-> filter={len(candidates)} ({', '.join(f'{k}={v}' for k, v in counts.items())}) "
          f"html_scans={_html_scans[0]}")
    print(f"[fetch] wrote {args.out}")


if __name__ == "__main__":
    main()
