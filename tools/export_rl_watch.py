#!/usr/bin/env python3
"""RL Watch / Lab export — TSF 레포에서 관리하는 공개 데이터 생성기.

XIF-RL/research_site 의 export_public.py 에서 복사해 온 것(원본은 XIF-RL에 그대로
둔다). 이 TSF 사본이 앞으로의 정본이며, 공개 RL Watch 스코프(어떤 논문을 실을지)는
여기서 관리한다.

동작(둘 다 이 레포 data/ 에 기록):
  data/rl_watch.json   triage 카드의 '정제' 공개 버전 — 논문 사실 필드만.
                       공개 스코프 = watch_type == 'rl_tsf' (TSF에 적용된 RL) 만.
                       연구 연결 필드(relevance/matched/watch_type/bigtech*)는 미노출.
  data/lab.enc.json    연구 노트(XIF-RL content/*.md + watch relevance 노트)를
                       PBKDF2-SHA256(600k) → AES-256-GCM 으로 암호화한 페이로드.

소스(비공개, 형제 XIF-RL 클론에서 읽기): research_site/watch/state/papers.json,
research_site/content/*.md. 평문 연구 내용은 이 스크립트 밖으로 나가지 않는다 —
공개 레포(TSF)에는 정제 카드 + 암호문만 기록한다.

패스프레이즈: env XIF_LAB_PASSPHRASE > ~/.lab_pass > ~/.xif_lab_pass.

사용:
  python tools/export_rl_watch.py                 # 형제 ../XIF-RL 에서 읽어 data/ 기록
  python tools/export_rl_watch.py --xif /path/to/XIF-RL/research_site
"""
import argparse
import base64
import json
import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent          # TSF/tools/
TSF_REPO = HERE.parent                           # TSF/
# 비공개 소스: 형제 XIF-RL 클론의 research_site (Win/Mac 공통 Desktop/Github 레이아웃)
DEFAULT_XIF_SITE = TSF_REPO.parent / "XIF-RL" / "research_site"
# 공용 ~/.lab_pass (lab-kit 표준, 모든 Lab 사이트 공유) 우선, 구 파일 fallback
PASS_FILES = [Path.home() / ".lab_pass", Path.home() / ".xif_lab_pass"]

PBKDF2_ITER = 600_000

# 공개 RL Watch 스코프: TSF에 적용된 RL 만. algo/tsf_trend/epi 는 제외.
PUBLIC_WATCH_TYPE = "rl_tsf"

# 공개 카드에 허용하는 필드만 명시 (allowlist — 새 필드가 생겨도 기본은 비공개)
PUBLIC_FIELDS = [
    "id", "title", "url", "repo", "published", "venue",
    "oneliner", "contribution", "strengths", "weaknesses",
    "category", "completeness",
]

# 정제 산출물에 있어선 안 되는 문자열 (연구 식별자 · 내부 표현)
DENYLIST = ["CRPO", "crpo", "XIF", "xif", "relevance", "우리 연구", "우리의", "본 연구"]

LAB_PAGE_ORDER = [
    "TSF_baselines_leaderboard.md",
    "CRPO_deepdive.md", "RL_algos.md", "comparison.md",
    "Time-R1_deepdive.md", "TimeMaster_deepdive.md",
]


def _read_passphrase():
    env = os.environ.get("XIF_LAB_PASSPHRASE")
    if env:
        return env
    for f in PASS_FILES:
        if f.exists():
            return f.read_text(encoding="utf-8").strip()
    sys.exit(f"[err] passphrase 없음: XIF_LAB_PASSPHRASE env 또는 {PASS_FILES[0]}")


def encrypt(payload: dict, passphrase: str) -> dict:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                     iterations=PBKDF2_ITER).derive(passphrase.encode("utf-8"))
    pt = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ct = AESGCM(key).encrypt(nonce, pt, None)  # ct||tag — WebCrypto 포맷과 동일
    return {
        "v": 1, "kdf": "PBKDF2-SHA256", "iter": PBKDF2_ITER,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def _scrub_text(s):
    """em-dash/·(중점)로 절을 나눠 DENYLIST(연구 식별자) 없는 절만 유지.
    strengths 의 '[논문 강점] — CRPO의 X와 통함' 에서 앞 절(논문 고유)만 남긴다."""
    parts = re.split(r"\s*[—–]\s*", str(s))
    kept = [seg.strip() for seg in parts if not any(w in seg for w in DENYLIST)]
    return " — ".join(kept).strip()


def _scrub_card(card):
    for f in ("oneliner", "contribution", "category"):
        if f in card:
            card[f] = _scrub_text(card[f])
    for f in ("strengths", "weaknesses"):
        if f in card:
            card[f] = [t for t in (_scrub_text(x) for x in card[f]) if t]
    return {k: v for k, v in card.items() if v not in (None, "", [])}


def sanitize_watch(papers: list) -> list:
    out = []
    for p in papers:
        if not p.get("oneliner"):               # 아직 triage 안 된 카드는 제외
            continue
        if p.get("watch_type") != PUBLIC_WATCH_TYPE:  # TSF에 적용된 RL 만 공개
            continue
        card = {k: p[k] for k in PUBLIC_FIELDS if p.get(k) not in (None, "", [])}
        out.append(_scrub_card(card))           # 연구 식별자 포함 절 자동 제거
    out.sort(key=lambda p: p.get("published", ""), reverse=True)
    return out


def check_denylist(text: str, label: str):
    hits = [w for w in DENYLIST if w in text]
    if hits:
        sys.exit(f"[LEAK-GUARD] {label} 에 금지 문자열 {hits} — export 중단. "
                 "해당 카드 필드를 수정하거나 Lab 쪽으로 옮길 것.")


def page_title(md: str, fallback: str) -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_lab_pages(papers: list, content: Path) -> list:
    pages = []
    names = [n for n in LAB_PAGE_ORDER if (content / n).exists()]
    names += sorted(p.name for p in content.glob("*.md") if p.name not in names)
    for name in names:
        md = (content / name).read_text(encoding="utf-8")
        pages.append({"id": name[:-3], "title": page_title(md, name[:-3]), "md": md})
    # watch relevance 노트 — 공개 카드에서 제거된 연구 연결 코멘트를 여기로
    rel = [p for p in papers if p.get("relevance")]
    if rel:
        lines = ["# Watch 연구 릴레번스 노트", "",
                 "공개 RL Watch 카드에서 분리된, 각 논문의 우리 연구와의 연결 메모.", ""]
        for p in sorted(rel, key=lambda x: x.get("published", ""), reverse=True):
            lines += [f"## {p['title']}",
                      f"[{p.get('id','')}]({p.get('url','')}) · {p.get('published','')[:10]}",
                      "", p["relevance"], ""]
        pages.append({"id": "watch_relevance", "title": "Watch 연구 릴레번스",
                      "md": "\n".join(lines)})
    return pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xif", default=os.environ.get("XIF_SITE", str(DEFAULT_XIF_SITE)),
                    help="비공개 XIF-RL research_site 경로 (default: 형제 ../XIF-RL/research_site)")
    args = ap.parse_args()

    xif = Path(args.xif)
    papers_path = xif / "watch" / "state" / "papers.json"
    content_dir = xif / "content"
    if not papers_path.exists():
        sys.exit(f"[err] 소스 papers.json 없음: {papers_path} (XIF-RL 클론이 형제 위치에 있어야 함)")

    data_dir = TSF_REPO / "data"
    papers = json.loads(papers_path.read_text(encoding="utf-8")).get("papers", [])

    # 1) 정제 공개 카드 (watch_type == rl_tsf 만)
    pub = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "papers": sanitize_watch(papers),
    }
    pub_text = json.dumps(pub, ensure_ascii=False, indent=1)
    check_denylist(pub_text, "rl_watch.json")
    (data_dir / "rl_watch.json").write_text(pub_text, encoding="utf-8")
    print(f"[watch] {len(pub['papers'])} cards (rl_tsf) → {data_dir / 'rl_watch.json'}")

    # 2) 암호화 Lab
    passphrase = _read_passphrase()
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "pages": build_lab_pages(papers, content_dir),
    }
    enc = encrypt(payload, passphrase)
    (data_dir / "lab.enc.json").write_text(
        json.dumps(enc, ensure_ascii=False, indent=1), encoding="utf-8")
    n = len(payload["pages"])
    kb = len(enc["ct"]) * 3 // 4 // 1024
    print(f"[lab] {n} pages encrypted ({kb} KB) → {data_dir / 'lab.enc.json'}")


if __name__ == "__main__":
    main()
