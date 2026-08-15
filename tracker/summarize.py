"""Deterministic card helpers for the leaderboard ingestion job.

Documented models remain pending for the Codex `tsf-cards` project skill.
Anonymous submissions receive a facts-only template without any model call.
"""


def template_card(name, info):
    """Build a facts-only card for submissions without public evidence."""
    gift = (info.get("stats") or {}).get("gift_eval") or {}
    rank = gift.get("rank_crps")
    position = f"GIFT-Eval average rank (CRPS) {rank:.1f}" if rank else "leaderboard entry"
    weaknesses = ["No public paper, model card, or code; architecture cannot be verified"]
    if info.get("testdata_leakage") == "Yes":
        weaknesses.append("The submission reports test-data leakage")
    return {
        "one_liner": "Anonymous or undocumented leaderboard submission",
        "summary": (
            f"No public paper, model card, or code is available. Current evidence: {position}. "
            "Only leaderboard measurements are reported."
        ),
        "arch_type": "Unknown",
        "org": info.get("org", ""),
        "strengths": [],
        "weaknesses": weaknesses,
        "paper_title": None,
        "paper_url": None,
        "is_documented": False,
    }


def has_evidence(info):
    """Return whether a documented model requires a Codex-authored card."""
    return bool(
        info.get("model_link")
        or info.get("code_link")
        or (info.get("stats") or {}).get("fev_bench")
    )
