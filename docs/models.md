# Models Summary Index

Architecture summaries for every model that has ever been evaluated in this
harness **or** referenced in `docs/sota_2026.md` / `docs/model_history.md`.

This index is maintained by the `tsf-scout` agent. Per-model deep dives live
under `docs/archs/<model>.md` — generated via `/explain-arch`.

## Registry

| Model | Year | Category | Params | Pretrained? | Paper | Arch doc |
|---|---|---|---|---|---|---|
| base (Seasonal Naive) | — | heuristic | 0 | no | — | [archs/base.md](archs/base.md) |
| Informer | 2021 | transformer | 11 M | no | [2012.07436](https://arxiv.org/abs/2012.07436) | _pending_ |
| Autoformer | 2021 | decomposition transformer | 14 M | no | [2106.13008](https://arxiv.org/abs/2106.13008) | _pending_ |
| DLinear / NLinear | 2023 | linear | < 1 M | no | [2205.13504](https://arxiv.org/abs/2205.13504) | _pending_ |
| PatchTST | 2023 | patch transformer | 7 M | optional SSL | [2211.14730](https://arxiv.org/abs/2211.14730) | _pending_ |
| TimesNet | 2023 | 2D conv (multi-period) | 5 M | no | [2210.02186](https://arxiv.org/abs/2210.02186) | _pending_ |
| iTransformer | 2024 | inverted attention | 4 M | no | [2310.06625](https://arxiv.org/abs/2310.06625) | _pending_ |
| Chronos | 2024 | foundation (tokenized T5) | 8 M – 710 M | yes | [2403.07815](https://arxiv.org/abs/2403.07815) | _pending_ |
| Chronos-Bolt / Chronos-2 | 2024-25 | foundation (distilled) | 9 M – 205 M | yes | — | _pending_ |
| Time-MoE (ultra) | 2024 | sparse MoE foundation | 24 M – 2.4 B active | yes | [2409.16040](https://arxiv.org/abs/2409.16040) | _pending_ |
| TimeExpert / TimeExpert-G | 2025 | MoE foundation | 113 M | yes | [2509.23145](https://arxiv.org/abs/2509.23145) | _pending_ |
| EMTSF | 2025 | ensemble MoE over SOTA backbones | 9.66 M | no | [2510.23396](https://arxiv.org/abs/2510.23396) | _pending_ |

Legend:
- **Pretrained?** — whether the model is a foundation model / uses SSL pretraining before the target benchmark
- **Arch doc** — `docs/archs/<name>.md` produced by `/explain-arch`; `_pending_` means not yet summarized

## Category rollup

- **Heuristic**: base (Seasonal Naive)
- **Linear**: DLinear, NLinear
- **Transformer (standard)**: Informer, Autoformer, PatchTST, TimesNet, iTransformer
- **Foundation (frozen / zero-shot)**: Chronos, Chronos-Bolt, Chronos-2, Time-MoE, TimeExpert-G
- **MoE / ensemble**: Time-MoE-ultra, TimeExpert, EMTSF

## How the index is updated

- `/explain-arch <arxiv_id>` produces a new `docs/archs/<name>.md`
- Run the `tsf-scout` agent to sweep arXiv and backfill `_pending_` entries
- New SOTA claims → additional entry in this table + an entry in `docs/sota_2026.md`

## How to evaluate a new model against the harness

1. Implement `models/<name>/predict.py` (see `models/base/predict.py`)
2. `python run.py --model <name>`
3. `python leaderboard.py` — refreshes `leaderboard.md`
4. Run `tsf-scout` (optional) to add the paper's SOTA reference numbers alongside
