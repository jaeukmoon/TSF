---
title: TimeExpert / TimeExpert-G
parent: Model Architectures
---

# TimeExpert / TimeExpert-G (2025)

**Paper**: [2509.23145](https://arxiv.org/abs/2509.23145)

## Structural features

- **MoE foundation model** — 113 M parameters; routing network picks domain-specific experts based on series characteristics (frequency, stationarity, cross-correlation signature).
- **Pretrained on UTSD-12G** corpus (12 B-token curated unified TSF dataset).
- **TimeExpert-G** = **G**eneralist variant with a short lookback (L=96) — optimized for zero-shot across unseen datasets.
- Uses a **patch + token** encoder similar to PatchTST as the backbone for each expert.

## Data flow

```
context → patch + embed
            │
            ▼
     [Router network computes expert weights]
            │
            ▼
    Sparse routing to top-k experts (per token)
            │
            ▼
     Weighted sum → horizon head → y_pred
```

## Why it mattered

- Strong zero-shot numbers at h=96 with only 113 M params (compare Time-MoE-ultra's 2.4 B total).
- Parameter-efficient frontier: currently competitive with Time-MoE on ETTh2, Weather, Exchange at zero shot.
- Domain-aware routing is a new design axis — prior MoE TSF models (Time-MoE) route per token, not per domain.

## Weaknesses

- Gap to supervised EMTSF remains on ECL / Traffic (multi-variate heavy).
- Expert specialization hard to interpret — "domain" labels are learned, not given.
