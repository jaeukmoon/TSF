---
title: Autoformer
parent: Model Architectures
---

# Autoformer (2021) — NeurIPS

**Paper**: [2106.13008](https://arxiv.org/abs/2106.13008)

## Structural features

- **Series decomposition block** — decomposes every intermediate representation into `trend + seasonal` using a moving average, inserted throughout the network (not only at input).
- **Auto-Correlation mechanism** — replaces self-attention. Computes time-delay similarity via FFT; aggregates information from **period-level** sub-series instead of per-token queries.
- **Decoder with progressive decomposition** — iteratively refines trend and seasonal predictions separately.

## Data flow

```
X → [Decomp]
     ├── trend_init → Linear   →   ┐
     └── seasonal    → Encoder(AutoCorr × N)
                       → Decoder(AutoCorr × M + cross-attn)
                       ⇓
                    seasonal_pred + trend_pred → Y
```

## Why it mattered

- Series decomposition became standard in every subsequent LTSF paper.
- AutoCorrelation shown to be more robust than attention on highly-periodic signals.

## Weaknesses

- Period estimation is brittle on short series.
- Later beaten by simple linear layers (DLinear, 2023) at comparable cost.
