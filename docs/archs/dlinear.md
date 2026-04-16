---
title: DLinear / NLinear
parent: Model Architectures
---

# DLinear & NLinear (2023) — AAAI

**Paper**: ["Are Transformers Effective for Time Series Forecasting?" 2205.13504](https://arxiv.org/abs/2205.13504)

## Structural features

- **One-layer linear model** — that's it. `Y = W · X + b` from input window to horizon.
- **DLinear**: decomposes input `X = trend + seasonal` via moving average, applies a separate linear layer to each component, then sums.
- **NLinear**: subtracts the last observation from `X` (normalizing), applies linear, then adds the last observation back.
- No attention, no non-linearity, no pretraining.

## Data flow

```
DLinear:
  X → [MA decomp] ── trend    → Linear_t ─┐
                  └─ seasonal → Linear_s ─┴─→ Y

NLinear:
  X → X - X[:, -1:]  → Linear → + X[:, -1:] → Y
```

## Why it mattered

- **Demolished** the narrative that transformers dominate LTSF. Beat Informer / Autoformer / FEDformer on all 8 LTSF datasets with orders-of-magnitude fewer parameters.
- Forced the field to reconsider inductive biases and evaluation protocols (lookback length sensitivity, normalization choices).

## Weaknesses

- No cross-series / cross-variable modeling — channel-independent by construction.
- Hits a ceiling on multivariate datasets with strong cross-channel signals (e.g., ECL, Traffic).
