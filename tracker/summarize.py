"""Generate Korean summary cards for newly detected leaderboard models.

Uses Claude Sonnet (claude-sonnet-5) via the official anthropic SDK with
structured outputs. If the SDK or ANTHROPIC_API_KEY is unavailable, callers
get None and the card stays pending until a later run.
"""

import json
import re
import urllib.parse
import xml.etree.ElementTree as ET

from common import http_get

SONNET = "claude-sonnet-5"

CARD_SCHEMA = {
    "type": "object",
    "properties": {
        "one_liner": {"type": "string", "description": "모델 한 줄 요약 (한국어, 기술용어는 영어)"},
        "summary": {"type": "string", "description": "3-5문장 요약: 아키텍처, 학습 방식, 왜 리더보드에서 이 성적인지 (한국어)"},
        "arch_type": {"type": "string", "description": "아키텍처 분류, 예: 'Transformer FM', 'MoE FM', 'SSM', 'Linear', 'Ensemble/Agentic', 'Statistical', 'Boosted Trees', 'Unknown'"},
        "org": {"type": "string", "description": "개발 조직 (모르면 빈 문자열)"},
        "strengths": {"type": "array", "items": {"type": "string"}, "description": "강점 1-3개 (한국어)"},
        "weaknesses": {"type": "array", "items": {"type": "string"}, "description": "약점/주의점 1-3개 (한국어, leakage 플래그 포함)"},
        "paper_title": {"type": ["string", "null"], "description": "실제 이 모델의 논문 제목. 후보 중 확실한 것이 없으면 null"},
        "paper_url": {"type": ["string", "null"], "description": "논문 URL. 확실한 것이 없으면 null"},
        "is_documented": {"type": "boolean", "description": "공개 논문/모델카드/코드 등 신뢰할 근거가 있으면 true, 익명 제출이면 false"},
    },
    "required": ["one_liner", "summary", "arch_type", "org", "strengths",
                 "weaknesses", "paper_title", "paper_url", "is_documented"],
    "additionalProperties": False,
}

SYSTEM = (
    "너는 시계열 예측(time-series forecasting) 벤치마크 트래커의 모델 요약카드 작성자다. "
    "제공된 근거(리더보드 성적, HuggingFace 모델카드, arXiv 후보 논문)만 사용해서 카드를 작성한다. "
    "근거에 없는 내용은 지어내지 않는다. 익명/미공개 제출이면 is_documented=false로 두고 "
    "리더보드 성적만으로 관찰 가능한 사실을 요약한다. "
    "arXiv 후보 논문은 이름이 비슷할 뿐 다른 모델일 수 있다 — 확실히 같은 모델일 때만 paper로 채택한다. "
    "모든 서술은 한국어, 기술 용어는 영어를 유지한다."
)


def search_arxiv(name):
    """Top-3 arXiv candidates for a model name. Returns list of dicts."""
    clean = re.sub(r"[_/]", " ", name)
    query = urllib.parse.quote(f'all:"{clean}" AND (cat:cs.LG OR cat:stat.ML)')
    url = f"http://export.arxiv.org/api/query?search_query={query}&max_results=3"
    try:
        root = ET.fromstring(http_get(url, retries=2).decode("utf-8"))
    except Exception as e:  # noqa: BLE001 - arXiv down must not block cards
        print(f"  [warn] arxiv search failed for {name}: {e}")
        return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for entry in root.findall("a:entry", ns):
        out.append({
            "title": " ".join(entry.findtext("a:title", "", ns).split()),
            "abstract": " ".join(entry.findtext("a:summary", "", ns).split())[:1500],
            "url": entry.findtext("a:id", "", ns),
        })
    return out


def fetch_hf_readme(model_link):
    """README of a huggingface.co model repo, truncated. None if not HF."""
    m = re.match(r"https?://huggingface\.co/([\w.-]+/[\w.-]+)/?$", model_link or "")
    if not m:
        return None
    try:
        text = http_get(f"https://huggingface.co/{m.group(1)}/raw/main/README.md",
                        retries=2).decode("utf-8", "replace")
        return text[:8000]
    except Exception:  # noqa: BLE001
        return None


def build_context(name, info):
    """Assemble the evidence block passed to Sonnet."""
    parts = [f"## 모델명\n{name}"]
    meta = {k: v for k, v in info.items() if k != "stats" and v}
    if meta:
        parts.append("## 리더보드 메타데이터\n" + json.dumps(meta, ensure_ascii=False, indent=2))
    if info.get("stats"):
        parts.append("## 리더보드 성적\n" + json.dumps(info["stats"], ensure_ascii=False, indent=2))
    readme = fetch_hf_readme(info.get("model_link"))
    if readme:
        parts.append("## HuggingFace 모델카드 (README)\n" + readme)
    candidates = search_arxiv(name)
    if candidates:
        parts.append("## arXiv 후보 논문 (동명이인일 수 있음)\n"
                     + json.dumps(candidates, ensure_ascii=False, indent=2))
    return "\n\n".join(parts)


def make_card(name, info):
    """Generate one card dict via Sonnet, or None if unavailable/failed."""
    try:
        import anthropic
    except ImportError:
        print("  [warn] anthropic SDK not installed; card pending")
        return None

    client = anthropic.Anthropic()
    context = build_context(name, info)
    try:
        response = client.messages.create(
            model=SONNET,
            max_tokens=4000,
            system=SYSTEM,
            output_config={"format": {"type": "json_schema", "schema": CARD_SCHEMA}},
            messages=[{"role": "user", "content":
                       f"다음 근거로 '{name}' 모델의 요약카드를 작성하라.\n\n{context}"}],
        )
    except anthropic.AuthenticationError:
        print("  [warn] ANTHROPIC_API_KEY missing/invalid; card pending")
        return None
    except anthropic.APIStatusError as e:
        print(f"  [warn] API error {e.status_code} for {name}; card pending")
        return None
    if response.stop_reason == "refusal":
        print(f"  [warn] refusal for {name}; card pending")
        return None
    text = next((b.text for b in response.content if b.type == "text"), "")
    return json.loads(text)
