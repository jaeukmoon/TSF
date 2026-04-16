"""LTSF 9종 벤치마크 러너 (datasetsforecast 포맷 기반).
데이터는 D:/BenchMark/tsf_data/ltsf/longhorizon/datasets/<GROUP>/ 에 위치.
각 GROUP 디렉토리에 M/ 또는 S/ 하위로 df_y.csv, df_x.csv 포함.
표준 split: train 70% / val 10% / test 20% (Autoformer 관례).
"""
import json
import os
from pathlib import Path
import numpy as np
import pandas as pd

from utils.metrics import mse, mae

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("TSF_DATA_DIR", ROOT / "datasets")) / "ltsf" / "longhorizon" / "datasets"

# (group_dir_name, kind, horizons, freq)
DATASETS = {
    "ETTh1":    ("ETTh1",    "S", [96, 192, 336, 720], "h"),
    "ETTh2":    ("ETTh2",    "S", [96, 192, 336, 720], "h"),
    "ETTm1":    ("ETTm1",    "M", [96, 192, 336, 720], "15min"),
    "ETTm2":    ("ETTm2",    "M", [96, 192, 336, 720], "15min"),
    "ECL":      ("ECL",      "M", [96, 192, 336, 720], "h"),
    "Exchange": ("Exchange", "M", [96, 192, 336, 720], "D"),
    "Traffic":  ("traffic",  "M", [96, 192, 336, 720], "h"),
    "Weather":  ("weather",  "M", [96, 192, 336, 720], "10min"),
    "ILI":      ("ili",      "M", [24, 36, 48, 60],    "W"),
}

CONTEXT_LEN = 512


def _load(group_dir, kind):
    path = DATA_DIR / group_dir / kind / "df_y.csv"
    df = pd.read_csv(path)
    # pivot to (time, channels)
    wide = df.pivot(index="ds", columns="unique_id", values="y").sort_index()
    return wide.values.astype(np.float32)


def _split(arr):
    n = len(arr)
    n_train = int(n * 0.7)
    n_test = int(n * 0.2)
    return arr[:n_train], arr[-n_test:]


def run(model_name, forecast_fn, out_dir):
    results = {}
    for ds, (group, kind, horizons, freq) in DATASETS.items():
        path = DATA_DIR / group / kind / "df_y.csv"
        if not path.exists():
            print(f"[skip] {ds}: {path} 없음")
            continue
        arr = _load(group, kind)
        _, test = _split(arr)
        for h in horizons:
            preds, trues = [], []
            for i in range(0, len(test) - CONTEXT_LEN - h + 1, h):
                ctx = test[i : i + CONTEXT_LEN].T
                y = test[i + CONTEXT_LEN : i + CONTEXT_LEN + h].T
                yhat = np.asarray(forecast_fn(ctx, h, freq))
                preds.append(yhat)
                trues.append(y)
            if not preds:
                continue
            preds = np.stack(preds)
            trues = np.stack(trues)
            r = {"mse": mse(trues, preds), "mae": mae(trues, preds),
                 "n_windows": len(preds), "horizon": h}
            key = f"{ds}_h{h}"
            results[key] = r
            out = out_dir / f"{key}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(r, indent=2))
            print(f"[{model_name}] {key}: MSE={r['mse']:.4f} MAE={r['mae']:.4f}")
    return results
