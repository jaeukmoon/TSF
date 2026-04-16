---
title: Chronos family
parent: Model Architectures
---

# Chronos (2024) + Chronos-Bolt / Chronos-2 (2024-25)

**Papers**:
- Chronos: [2403.07815](https://arxiv.org/abs/2403.07815) — AWS AI Labs
- Chronos-Bolt / Chronos-2: model cards on HuggingFace (distillation + multi-horizon)

## Chronos (original)

- **Tokenize continuous values** — scale the series into a fixed range and bin into 4,096 tokens.
- Use a **vanilla T5 encoder-decoder** (sizes: Tiny 8M / Mini 20M / Small 46M / Base 200M / Large 710M) over the token stream.
- **Training data**: C4-scale synthetic time series (Gaussian processes, harmonic mixtures) + real datasets. No task-specific supervision.
- **Inference**: autoregressive token-by-token sampling → probabilistic forecast.

### Data flow

```
x_t  →  scale to [-15, 15]  →  quantize to token id in {0..4095}
                           │
                           ▼
              [T5 encoder-decoder]
                           │
                           ▼
        autoregressive token ids → de-quantize → y_t+1..t+H
```

## Chronos-Bolt (2024)

- **Distilled** Chronos T5 → smaller, faster encoder-only model.
- **Direct multi-horizon head** — emits the full horizon in one forward pass (no autoregression).
- 5–250× faster than original Chronos at similar accuracy.

## Chronos-2 (2025)

- **Multi-variate-aware** — handles multiple related series in a single context.
- Larger training corpus, better covariate conditioning.
- Current SOTA (as of this repo's `docs/sota_2026.md`) on LLM-based zero-shot LTSF benchmarks.

## Why the family matters

- First wave of genuinely useful zero-shot TSF foundation models.
- Made tokenize-and-transformer a viable TSF recipe.
- Chronos-Bolt's direct-horizon head killed the latency argument against foundation models.

## Weaknesses

- Value tokenization caps resolution (4,096 bins). For highly continuous series the discretization error is non-trivial.
- Chronos-1 is slow; Chronos-Bolt/2 partly address but still slower than task-specific PatchTST at matched accuracy.
