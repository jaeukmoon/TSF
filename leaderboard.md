---
title: Leaderboard
layout: default
nav_order: 2
---

# TSF Benchmark — Leaderboard
{: .no_toc }

_Auto-generated. Last update: 2026-04-14_

Cells: `MSE / MAE` (lower is better). Columns = dataset, rows = model.
Separate table per forecasting horizon.

---

## Horizon = 96

| Model | ETTh1 | ETTh2 | ETTm1 | ETTm2 | ECL | Exchange | Traffic | Weather |
|---|---|---|---|---|---|---|---|---|
| base (Seasonal Naive) | 0.0723 / 0.2130 | 0.1486 / 0.3012 | 1.0760 / 0.6379 | 0.3422 / 0.3760 | 0.3469 / 0.3352 | 0.0874 / 0.2095 | 1.2334 / 0.5149 | 0.2463 / 0.2424 |

## Horizon = 192

| Model | ETTh1 | ETTh2 | ETTm1 | ETTm2 | ECL | Exchange | Traffic | Weather |
|---|---|---|---|---|---|---|---|---|
| base (Seasonal Naive) | 0.0903 / 0.2363 | 0.1625 / 0.3171 | 1.0968 / 0.6490 | 0.3627 / 0.3915 | 0.3035 / 0.3230 | 0.1560 / 0.2828 | 1.1272 / 0.4756 | 0.3067 / 0.2834 |

## Horizon = 336

| Model | ETTh1 | ETTh2 | ETTm1 | ETTm2 | ECL | Exchange | Traffic | Weather |
|---|---|---|---|---|---|---|---|---|
| base (Seasonal Naive) | 0.1341 / 0.2966 | 0.2955 / 0.4538 | 0.9988 / 0.6363 | 0.3534 / 0.3834 | 0.2996 / 0.3284 | 0.2379 / 0.3501 | 1.3883 / 0.5472 | 0.3433 / 0.3248 |

## Horizon = 720

| Model | ETTh1 | ETTh2 | ETTm1 | ETTm2 | ECL | Exchange | Traffic | Weather |
|---|---|---|---|---|---|---|---|---|
| base (Seasonal Naive) | 0.1620 / 0.3358 | 0.3022 / 0.4354 | 0.9470 / 0.6279 | 0.6615 / 0.5211 | 0.3540 / 0.3702 | 0.9984 / 0.7859 | 1.2996 / 0.5294 | 0.4904 / 0.4033 |

---

## Evaluated models

| Key | Type | Source |
|---|---|---|
| base | Seasonal Naive baseline | `models/base/predict.py` |

> Add your model under `models/<name>/` → `python run.py --model <name>` → `python leaderboard.py`. A new row will appear in each horizon table above.

## Published SOTA reference (h=96)

Top numbers reported in published papers (not re-measured here). See [docs/sota_2026.md](docs/sota_2026.md) for full tables and horizon × 192/336/720.

| Metric | ETTh1 | ETTh2 | ETTm1 | ETTm2 | ECL | Exchange | Traffic | Weather |
|---|---|---|---|---|---|---|---|---|
| Best MSE@96 | 0.323 | **0.262** | 0.256 | **0.156** | **0.126** | 0.086 | **0.343** | 0.138 |
| Model | Time-MoE-ultra | EMTSF | Time-MoE-ultra | EMTSF | EMTSF | iTransformer | EMTSF | EMTSF |
| Paper | [2409.16040](https://arxiv.org/abs/2409.16040) | [2510.23396](https://arxiv.org/abs/2510.23396) | [2409.16040](https://arxiv.org/abs/2409.16040) | [2510.23396](https://arxiv.org/abs/2510.23396) | [2510.23396](https://arxiv.org/abs/2510.23396) | [2310.06625](https://arxiv.org/abs/2310.06625) | [2510.23396](https://arxiv.org/abs/2510.23396) | [2510.23396](https://arxiv.org/abs/2510.23396) |

**Bold** = this cell is the current published SOTA and the model in the row below can be directly compared only under matching lookback/split. Mixing lookback lengths across papers is **not** apples-to-apples.

## Caveats

Harness numbers (base row) use lookback=96 and the `datasetsforecast` LongHorizon default split. Published numbers may use L=336 / 512 and custom normalization, so **do not compare directly** without reconciling the pipeline.

See also: [docs/model_history.md](docs/model_history.md), [docs/ili_lineage.md](docs/ili_lineage.md)
