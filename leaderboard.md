# TSF Benchmark — Leaderboard

_Auto-generated. Last update: 2026-04-14_

## Evaluated models (1)
- **base** — Seasonal Naive (`models/base/predict.py`). Reference adapter, weak baseline.

## Datasets & horizons
- LTSF 8: ETTh1, ETTh2, ETTm1, ETTm2, ECL, Exchange, Traffic, Weather
- Horizons: [96, 192, 336, 720]
- Metric cells: `MSE / MAE` (lower = better). `n_windows` noted per dataset.

---

### ETTh1  (n_windows ≈ 24)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.0723 / 0.2130 | 0.0903 / 0.2363 | 0.1341 / 0.2966 | 0.1620 / 0.3358 |

### ETTh2  (n_windows ≈ 24)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.1486 / 0.3012 | 0.1625 / 0.3171 | 0.2955 / 0.4538 | 0.3022 / 0.4354 |

### ETTm1  (n_windows ≈ 114)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 1.0760 / 0.6379 | 1.0968 / 0.6490 | 0.9988 / 0.6363 | 0.9470 / 0.6279 |

### ETTm2  (n_windows ≈ 114)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.3422 / 0.3760 | 0.3627 / 0.3915 | 0.3534 / 0.3834 | 0.6615 / 0.5211 |

### ECL  (n_windows ≈ 49)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.3469 / 0.3352 | 0.3035 / 0.3230 | 0.2996 / 0.3284 | 0.3540 / 0.3702 |

### Exchange  (n_windows ≈ 10)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.0874 / 0.2095 | 0.1560 / 0.2828 | 0.2379 / 0.3501 | 0.9984 / 0.7859 |

### Traffic  (n_windows ≈ 31)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 1.2334 / 0.5149 | 1.1272 / 0.4756 | 1.3883 / 0.5472 | 1.2996 / 0.5294 |

### Weather  (n_windows ≈ 104)

| Model | h=96 (MSE/MAE) | h=192 (MSE/MAE) | h=336 (MSE/MAE) | h=720 (MSE/MAE) |
|---|---|---|---|---|
| base (SN) | 0.2463 / 0.2424 | 0.3067 / 0.2834 | 0.3433 / 0.3248 | 0.4904 / 0.4033 |

---

## Caveats

Numbers above are from this harness's evaluation pipeline (lookback=96, n_windows as produced by the built-in split). They are **not directly comparable** to published numbers in PatchTST / iTransformer / Time-MoE / EMTSF without reconciling:
- train/val/test cutoffs  
- lookback length  
- per-channel vs global normalization  
- rolling-origin vs fixed-origin evaluation

For the published SOTA reference, see:
- [docs/sota_2026.md](docs/sota_2026.md) — EMTSF, TimeExpert, Time-MoE-ultra current leaders (Oct 2025)
- [docs/model_history.md](docs/model_history.md) — 2021–2026 LTSF model lineage
- [docs/ili_lineage.md](docs/ili_lineage.md) — ILI-specific model history

## How to add your model

See [README.md § Model Interface](README.md#model-interface). In short: drop a `predict.py` with `forecast(context, horizon, freq)` into `models/<your_name>/`, run `python run.py --model <your_name>`, then `python leaderboard.py` to refresh this table.