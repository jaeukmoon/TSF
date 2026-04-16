---
title: TimesNet
parent: Model Architectures
---

# TimesNet (2023) — ICLR

**Paper**: [2210.02186](https://arxiv.org/abs/2210.02186)

## Structural features

- **1D → 2D reshape** — detect dominant periods via FFT and fold the 1D series into a 2D tensor where rows are periods and columns are intra-period positions.
- **Inception-style 2D convolution** (TimesBlock) on the reshaped tensor captures both **intra-period** and **inter-period** variations.
- **Adaptive aggregation** — weight outputs from multiple detected periods by their FFT amplitudes.
- Unified across 5 time-series tasks (forecasting, imputation, classification, anomaly, segmentation).

## Data flow

```
X (1D) ─FFT→ pick top-k periods p_1..p_k
           │
           ├── reshape to (p_i, L/p_i)  for each i
           │       │
           │       ▼
           │   Inception2D conv blocks
           │       │
           │       ▼
           │  reshape back to 1D
           │
           └─ weighted sum by FFT amplitudes → Y
```

## Why it mattered

- Clever way to reuse strong 2D vision backbones (Inception) for time series.
- Gave decent numbers across tasks without task-specific architecture.

## Weaknesses

- FFT-period detection unstable on non-stationary data (Exchange).
- Beaten by PatchTST on pure long-horizon forecasting.
