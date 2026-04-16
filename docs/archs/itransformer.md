---
title: iTransformer
parent: Model Architectures
---

# iTransformer (2024) — ICLR

**Paper**: [2310.06625](https://arxiv.org/abs/2310.06625)

## Structural features

- **Inverted dimensions** — the entire time dimension of each variate becomes a **single token embedding**. Attention operates across **variates** (channels), not across time steps.
- **Time-mixing via feed-forward** — temporal dependencies handled inside the per-variate MLP, while attention focuses on cross-variate relationships.
- Drop-in replacement for vanilla transformer — no bells and whistles.

## Data flow

```
Input  (B, L, C)
         │
         ▼
    (B, C, d)  per-variate linear embedding of the L-length series
         │
         ▼
  Transformer encoder  (attention across C variates)
         │
         ▼
    Linear projection from d → horizon
         │
         ▼
Output  (B, horizon, C)
```

Contrast with vanilla/PatchTST where attention is **across time tokens**.

## Why it mattered

- Cleanly explains what transformers *should* do for MTS: model **variate relationships**, not temporal ones.
- Matched PatchTST on LTSF 8 with a much simpler design; SOTA on multi-variate datasets (ECL, Traffic).

## Weaknesses

- No explicit long-horizon mechanism — relies on the per-variate MLP's ability to project the full L-length representation.
- Zero-shot transfer weak; needs per-dataset training.
