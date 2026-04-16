---
title: Informer
parent: Model Architectures
---

# Informer (2021) — AAAI Best Paper

**Paper**: [2012.07436](https://arxiv.org/abs/2012.07436)
**Code**: [zhouhaoyi/Informer2020](https://github.com/zhouhaoyi/Informer2020)

## Structural features

- **ProbSparse self-attention** — `O(L log L)` instead of `O(L²)`. Sub-samples keys by KL-divergence of query-key distribution; keeps only top-`u` "active" queries.
- **Self-attention distilling** — halves sequence length between encoder layers via `MaxPool(Conv1D)`, pyramid-style.
- **Generative-style decoder** — one-pass forward generation of the whole horizon (not autoregressive), reducing inference latency.
- **Time-feature embedding** — explicit positional + calendar features (month / day / weekday / hour).

## Data flow

```
X_enc (L_in, d)  ──► TokenEmb + PosEmb + TimeEmb
                      │
                      ▼
              Encoder: [ProbSparse → Distill ] × N
                      │
                      ▼
           Decoder:  concat(X_token, 0-pad)
                    → MaskedAttn → CrossAttn → Linear
                      │
                      ▼
              Y_pred  (horizon, d)
```

## Why it mattered

- First transformer to handle long horizons (L=720) without blowing up memory.
- Baseline for every subsequent LTSF paper through 2024.

## Known weaknesses

- ProbSparse under-performs simple Autoformer decomposition on trend-heavy data.
- Reported numbers are often *worse* than DLinear (2023) at the same setting — motivating Zeng et al.'s critique.
