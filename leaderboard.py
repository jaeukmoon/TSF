"""results/ 를 스캔해서 leaderboard.md 자동 생성."""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def collect():
    table = defaultdict(dict)  # table[(bench,dataset_h)][model] = metric dict
    for model_dir in sorted(RESULTS.glob("*/")):
        model = model_dir.name
        for bench_dir in model_dir.glob("*/"):
            bench = bench_dir.name
            for f in bench_dir.glob("*.json"):
                key = (bench, f.stem)
                table[key][model] = json.loads(f.read_text())
    return table


def render(table):
    if not table:
        return "# Leaderboard\n\n_결과 없음. `python run.py --model <name>` 실행._\n"
    models = sorted({m for v in table.values() for m in v})
    lines = ["# Leaderboard", ""]
    lines.append("| Benchmark | Dataset | Metric | " + " | ".join(models) + " |")
    lines.append("|" + "---|" * (3 + len(models)))
    for (bench, ds), row in sorted(table.items()):
        for metric in ("mse", "mae", "mase", "crps"):
            if not any(metric in v for v in row.values()):
                continue
            cells = [f"{row[m][metric]:.4f}" if m in row and metric in row[m] else "—"
                     for m in models]
            lines.append(f"| {bench} | {ds} | {metric.upper()} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    out = ROOT / "leaderboard.md"
    out.write_text(render(collect()))
    print(f"wrote {out}")
