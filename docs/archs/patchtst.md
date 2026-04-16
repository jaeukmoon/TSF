---
title: PatchTST
parent: Model Architectures
---

# PatchTST (2023) — ICLR

**Paper**: [2211.14730](https://arxiv.org/abs/2211.14730)
**Code**: [yuqinie98/PatchTST](https://github.com/yuqinie98/PatchTST)

## Structural features

- **Patching** — split the input series into non-overlapping (or overlapping, stride < length) patches of length `P`. Each patch becomes a single token. Drastically cuts sequence length (e.g., 336 time steps → 42 patches with P=16, stride=8).
- **Channel-independence** — each variate's series is processed **independently** by the same transformer; covariance between channels is not modeled.
- **Standard transformer encoder** on top of patch tokens → linear projection to horizon.
- **Optional SSL pretraining**: mask-and-reconstruct patches before supervised fine-tuning.

## Data flow

```
(B, C, L)  ──patchify──►  (B, C, N, P)        # N patches of length P
                │
                ▼
         (B·C, N, d_model) via per-patch linear embedding
                │
                ▼
          Transformer encoder × N_layers
                │
                ▼
         linear head → (B, C, horizon)
```

## Why it mattered

- Finally gave transformers a **clean win** over DLinear across LTSF 8.
- "Channel independence + long lookback" has been the dominant recipe since 2023. iTransformer, Time-MoE, EMTSF all cite PatchTST as the patch convention source.

## Weaknesses

- Channel independence limits performance when cross-channel structure matters (ECL at long horizons, Traffic).
- Hyperparameter-sensitive (patch length, stride, lookback).
