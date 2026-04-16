"""단일 모델 전체 벤치마크 실행."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.registry import load_model, list_models
from benchmarks import ltsf, gift_eval


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="models/<name>/ 디렉토리 이름")
    p.add_argument("--benchmarks", nargs="+", default=["ltsf", "gift_eval"],
                   choices=["ltsf", "gift_eval"])
    args = p.parse_args()

    if args.model not in list_models():
        print(f"등록된 모델: {list_models()}")
        sys.exit(1)

    fn = load_model(args.model)
    out_root = ROOT / "results" / args.model
    summary = {}

    if "ltsf" in args.benchmarks:
        summary["ltsf"] = ltsf.run(args.model, fn, out_root / "ltsf")
    if "gift_eval" in args.benchmarks:
        summary["gift_eval"] = gift_eval.run(args.model, fn, out_root / "gift_eval")

    (out_root / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n결과 저장: {out_root}")


if __name__ == "__main__":
    main()
