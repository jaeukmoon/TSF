---
title: FEDformer
parent: Model Architectures
---

# FEDformer (2022) — ICML

**Paper**: [2201.12740](https://arxiv.org/abs/2201.12740)

## Structural features

- **Frequency-enhanced blocks** — self-attention operates in the **frequency domain** via Fourier (FEB-f) or wavelet (FEB-w) basis.
- **Random sub-sampling** in frequency — only a small set of frequency modes are used, giving linear complexity and implicit low-rank regularization.
- **Mixture of Experts** for decomposition — learns a mix of moving-average kernels instead of one fixed kernel.

## Data flow

```
X → MoE-decomp → {trend, seasonal}
                   │
seasonal ── FEB-f (FFT → keep random M modes → iFFT) ── Decoder
trend    ── linear projection                     ───┘
```

## Why it mattered

- First to show that working in frequency space drastically cuts memory on long horizons.
- Random mode sampling served as a strong inductive bias + regularizer.

## Weaknesses

- Performance gap over Autoformer/PatchTST has narrowed; rarely SOTA after 2023.
- Frequency-mode selection adds a hyperparameter surface.
