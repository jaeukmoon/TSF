---
title: Home
layout: default
nav_order: 1
---

# TSF Benchmark Harness

A **plug-and-play evaluation framework** for time-series forecasting foundation models.
Register a single `forecast()` function and get LTSF + GIFT-Eval scores + an auto-generated leaderboard.

📊 **Current leaderboard**: [leaderboard.md](leaderboard.md)
📚 **Model lineage & SOTA reference**: [docs/sota_2026.md](docs/sota_2026.md), [docs/model_history.md](docs/model_history.md)
🧩 **All models (architectures)**: [docs/models.md](docs/models.md) — per-model summaries in [docs/archs/](docs/archs/)
🤖 **Auto-update agent**: [`tsf-scout`](.claude/agents/tsf-scout.md) — scans arXiv, updates SOTA docs + leaderboard reference

---

## What it does

| Component | Role |
|---|---|
| `models/<name>/predict.py` | Your model — a single `forecast(context, horizon, freq)` function |
| `benchmarks/ltsf.py` | Evaluates on LTSF 8 (ETTh1/2, ETTm1/2, ECL, Exchange, Traffic, Weather) |
| `benchmarks/gift_eval.py` | Evaluates on GIFT-Eval (23 datasets, Salesforce 2024) |
| `utils/metrics.py` | MSE / MAE / MASE / CRPS implementations |
| `run.py` | One-shot driver: `python run.py --model <name>` |
| `leaderboard.py` | Regenerates `leaderboard.md` from `results/` |

## Benchmark targets

### LTSF 8 (standard, Autoformer / TimesNet / PatchTST lineage)
- **Datasets**: ETTh1, ETTh2, ETTm1, ETTm2, Weather, Electricity (ECL), Traffic, Exchange
- **Horizons**: {96, 192, 336, 720} (for ILI: {24, 36, 48, 60})
- **Metrics**: MSE, MAE

### GIFT-Eval (Salesforce 2024)
- 23 datasets × multiple frequencies
- Metrics: MASE, CRPS (+ optional WQL)

## Data hosting

GitHub blocks files > 100 MB, so datasets live on a mirrored HuggingFace repo:

```bash
# First-time mirror upload (one machine):
export TSF_DATA_DIR="D:/Users/tsf_data"       # optional — defaults to datasets/
huggingface-cli login
bash datasets/mirror_upload.sh                # default repo: Yotto3108/tsf-benchmarks

# Every other machine: just download
bash datasets/download_all.sh
```

## Usage

```bash
# 1. Download data (one-time)
export TSF_DATA_DIR="D:/Users/tsf_data"
bash datasets/download_all.sh

# 2. Register a new model
mkdir -p models/my_model
cp models/base/predict.py models/my_model/predict.py   # adapt forecast()

# 3. Run the full suite
python run.py --model my_model

# 4. Refresh leaderboard
python leaderboard.py
```

## Model interface

Every model exposes a single function:

```python
def forecast(context: np.ndarray, horizon: int, freq: str) -> np.ndarray:
    """
    context : (n_series, context_len)  or  (context_len,)
    horizon : int   — forecast length
    freq    : str   — 'h', 'D', 'W', ...

    Returns
    -------
    (n_series, horizon) or (horizon,) point forecasts.
    Probabilistic models may return (n_series, horizon, n_samples).
    """
```

See `models/base/predict.py` for the Seasonal Naive reference implementation.

## Repository layout

```
TSF/
├── datasets/
│   ├── ltsf/                   # ETTh/ETTm/Weather/ECL/Traffic/ILI/Exchange
│   ├── gift_eval/              # HF caches
│   └── download_all.sh
├── models/
│   ├── base/predict.py         # reference: seasonal naive
│   └── <your_model>/predict.py
├── benchmarks/
│   ├── ltsf.py
│   └── gift_eval.py
├── utils/
│   ├── metrics.py              # MSE / MAE / MASE / CRPS
│   └── registry.py
├── results/<model>/<bench>/<dataset>_<horizon>.json
├── leaderboard.md              # auto-generated — see top of repo
├── docs/
│   ├── model_history.md        # 2021–2026 LTSF model lineage
│   ├── sota_2026.md            # current SOTA (EMTSF, TimeExpert, Time-MoE-ultra)
│   └── ili_lineage.md          # ILI model history (CNNRNN-Res → MPSTAN)
└── run.py
```

## Current leaderboard (preview — MSE only)

Only the Seasonal Naive baseline is committed so far. Full MSE+MAE per horizon: [leaderboard.md](leaderboard.md).

| Dataset | h=96 | h=192 | h=336 | h=720 |
|---|---|---|---|---|
| ETTh1 | 0.0723 | 0.0903 | 0.1341 | 0.1620 |
| ETTh2 | 0.1486 | 0.1625 | 0.2955 | 0.3022 |
| ETTm1 | 1.0760 | 1.0968 | 0.9988 | 0.9470 |
| ETTm2 | 0.3422 | 0.3627 | 0.3534 | 0.6615 |
| ECL | 0.3469 | 0.3035 | 0.2996 | 0.3540 |
| Exchange | 0.0874 | 0.1560 | 0.2379 | 0.9984 |
| Traffic | 1.2334 | 1.1272 | 1.3883 | 1.2996 |
| Weather | 0.2463 | 0.3067 | 0.3433 | 0.4904 |

> **Caveat**: these come from this harness's pipeline (lookback=96, built-in split). They are **not directly comparable** to PatchTST / iTransformer / Time-MoE / EMTSF published numbers — see [leaderboard.md § Caveats](leaderboard.md#caveats).

## License

MIT.
