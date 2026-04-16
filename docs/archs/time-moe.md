---
title: Time-MoE
parent: Model Architectures
---

# Time-MoE (2024)

**Paper**: [2409.16040](https://arxiv.org/abs/2409.16040)

## Structural features

- **Sparse Mixture-of-Experts** decoder-only transformer. Total params up to 2.4 B; **~24 M active** per token.
- **Point-forecast head** (not tokenized / quantized) — regression directly on scaled values. Avoids Chronos-style bin quantization error.
- **Pretrained on Time-300B** corpus — the largest public TSF pretraining set (300 B time-steps of diverse series).
- **Time-MoE-ultra** variant: the setting reported in `docs/sota_2026.md` tables. Uses lookback L=512.

## Data flow

```
context → [scale / normalize]
            │
            ▼
  [decoder-only transformer with MoE FFN blocks]
      (router picks top-k experts per token)
            │
            ▼
     linear projection to H future values
            │
            ▼
          y_t+1..t+H  (point forecast)
```

## Why it mattered

- First non-tokenized foundation model to match task-specific SOTA on LTSF with zero shots.
- Still holds best numbers on several ETTh1 / ETTm1 settings (h=96) as of late 2025.
- Demonstrated that **sparse scaling** beats dense scaling for TSF (unlike Chronos).

## Weaknesses

- MoE routing adds deployment complexity (expert sharding at inference).
- 2.4 B total params is painful for CPU-only environments.
- Loses to EMTSF on ETTh2/ETTm2/ECL at h=96 (see sota_2026.md).
