---
title: EMTSF
parent: Model Architectures
---

# EMTSF — "Extraordinary Mixture of SOTA Models" (2025)

**Paper**: [2510.23396](https://arxiv.org/abs/2510.23396)
**Setting**: supervised, L=512, 9.66 M parameters

## Structural features

- **Ensemble + MoE gating over existing SOTA backbones** (PatchTST, iTransformer, Time-MoE, etc.) rather than a new monolithic architecture.
- **Gating network** — learns per-sample weights over the backbone pool. Input features include series statistics (mean, variance, autocorrelation at known periods).
- **Joint fine-tune** — backbones start frozen; gating is learned first, then a final round jointly fine-tunes gating + light adapters on each backbone.
- Small parameter budget (9.66 M) because the backbones are shared across samples and the gating net is tiny.

## Data flow

```
X ──┬── PatchTST  → y_pt
    ├── iTransformer → y_it
    ├── Time-MoE-ultra → y_moe
    │
    └── Gating MLP (stats) → weights (w_pt, w_it, w_moe, ...)
                                   │
                                   ▼
                          y = Σ  w_i · y_i  → Y
```

## Why it mattered

- **New SOTA** at h=96 on **ETTh2 (0.262), ETTm2 (0.156), ECL (0.126), Traffic (0.343)** (see `docs/sota_2026.md`).
- Shows that **how you combine** existing backbones matters more than inventing a new one.
- Lightweight: 9.66 M params beating 2.4 B-param Time-MoE-ultra on these datasets.

## Weaknesses

- Relies on availability of strong pretrained backbones — not an end-to-end solution.
- Still underperforms Time-MoE-ultra on ETTh1 (0.359 vs 0.323) — gating doesn't save it when no backbone is strong on that data.
- Less studied at h ≥ 192.
