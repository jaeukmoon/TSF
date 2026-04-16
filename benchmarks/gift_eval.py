"""GIFT-Eval 러너 (stub).
TODO: Salesforce/GiftEval 로더 규격 확정 후 채우기 — 공식 레포의 평가 루틴 이식 예정.
현재는 datasets/gift_eval 캐시가 있으면 데이터셋 목록만 훑는다.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import os
DATA_DIR = Path(os.environ.get("TSF_DATA_DIR", ROOT / "datasets")) / "gift_eval"


def run(model_name, forecast_fn, out_dir):
    if not DATA_DIR.exists():
        print(f"[gift_eval] {DATA_DIR} 없음 — download_all.sh 먼저 실행.")
        return {}
    print(f"[gift_eval] TODO: 공식 평가 루틴 이식 필요. 현재 stub.")
    return {}
