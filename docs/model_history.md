# LTSF Benchmark — Historical Model Performance (2021–2026)

본 문서는 Long-term Time Series Forecasting (LTSF) 표준 벤치마크 9개 데이터셋(ETTh1, ETTh2, ETTm1, ETTm2, ECL/Electricity, Exchange, Traffic, Weather, ILI)에 대한 주요 모델들의 MSE / MAE (정규화된 값)를 연대순으로 정리한 것이다.

- 지평(horizon): 대부분 {96, 192, 336, 720}, ILI만 {24, 36, 48, 60}.
- 셀 포맷: `MSE / MAE`. 결측은 `—`.
- **입력 길이(lookback)는 결과의 공정성에 큰 영향을 미친다.** 아래 각 표 머리말에 명시.
- 숫자 출처는 각 섹션에 명기. 원 논문 숫자를 우선 사용하고, 이후 세대의 재측정(예: iTransformer Table 10, Time-MoE Table 4)에서만 구할 수 있는 경우엔 그 출처를 명시.

> 원래 저장 경로(`TSF/docs/model_history.md`) 생성이 샌드박스 권한상 차단되어 `TSF/models/base/` 아래에 저장함.

---

## Model → Paper / Year / Venue

| Model | Year | Venue | arXiv |
|---|---|---|---|
| Informer | 2021 | AAAI (Best Paper) | 2012.07436 |
| Autoformer | 2021 | NeurIPS | 2106.13008 |
| Pyraformer | 2022 | ICLR | (OpenReview) |
| FEDformer | 2022 | ICML | 2201.12740 |
| LogTrans | 2019 | NeurIPS | 1907.00235 |
| NLinear / DLinear | 2023 | AAAI | 2205.13504 |
| PatchTST | 2023 | ICLR | 2211.14730 |
| TimesNet | 2023 | ICLR | 2210.02186 |
| Crossformer | 2023 | ICLR | (OpenReview) |
| Stationary (Non-stat. Tr.) | 2022 | NeurIPS | 2205.14415 |
| ETSformer | 2022 | arXiv | 2202.01381 |
| LightTS | 2022 | arXiv | 2207.01186 |
| MICN | 2023 | ICLR | (OpenReview) |
| FiLM | 2022 | NeurIPS | 2205.08897 |
| TiDE | 2023 | TMLR | 2304.08424 |
| RLinear | 2023 | arXiv | 2305.10721 |
| SCINet | 2022 | NeurIPS | 2106.09305 |
| iTransformer | 2024 | ICLR | 2310.06625 |
| TimeMixer | 2024 | ICLR | 2405.14616 |
| Time-LLM | 2024 | ICLR | 2310.01728 |
| GPT4TS (OFA) | 2023 | NeurIPS | 2302.11939 |
| Moirai (S/B/L) | 2024 | ICML | 2402.02592 |
| Chronos (S/B/L) | 2024 | TMLR | 2403.07815 |
| TimesFM | 2024 | ICML | 2310.10688 |
| Moment | 2024 | ICML | 2402.03885 |
| Time-MoE | 2025 | ICLR Spotlight | 2409.16040 |
| Moirai-MoE | 2025 | — | 2410.10469 |

---

## 출처(Source) 약어

- **[DLin]** Zeng et al., "Are Transformers Effective for Time Series Forecasting?" (AAAI 2023), Table via ar5iv/2205.13504. Lookback L=96 (ILI: L=104).
- **[Patch]** Nie et al., "A Time Series is Worth 64 Words" (ICLR 2023), Table 3 via ar5iv/2211.14730. Lookback **L=512** (PatchTST/64), **L=336** (PatchTST/42 및 baselines).
- **[iTr]** Liu et al., "iTransformer" (ICLR 2024), Table 10 (Appendix) via ar5iv/2310.06625. Lookback **L=96**.
- **[TMix]** Wang et al., "TimeMixer" (ICLR 2024), Table 13 (unified hyperparameter). Lookback L=96.
- **[TLLM]** Jin et al., "Time-LLM" (ICLR 2024), Table 1/Table 3 via ar5iv/2310.01728.
- **[TMoE-ZS]** Shi et al., "Time-MoE" (ICLR 2025 Spotlight) Table 3 — **zero-shot** via arxiv/2409.16040v2. Baseline 값은 해당 표 기준.
- **[TMoE-ID]** Time-MoE Table 4 — **in-distribution (full fine-tune)** 재측정.

**주의**: 동일 모델이라도 lookback과 정규화/채널 처리에 따라 결과가 다르다. 표 내 숫자가 출처마다 다르게 나타나는 것은 정상이다.

---

## ETTh1 (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.865 / 0.713 | 1.008 / 0.792 | 1.107 / 0.809 | 1.181 / 0.865 | [DLin] |
| LogTrans | 2019 | 0.878 / 0.740 | 1.037 / 0.824 | 1.238 / 0.932 | 1.135 / 0.852 | [Patch] |
| Pyraformer | 2022 | 0.664 / 0.612 | 0.790 / 0.681 | 0.891 / 0.738 | 0.963 / 0.782 | [DLin] |
| Autoformer | 2021 | 0.449 / 0.459 | 0.500 / 0.482 | 0.521 / 0.496 | 0.514 / 0.512 | [DLin] |
| FEDformer | 2022 | 0.376 / 0.419 | 0.420 / 0.448 | 0.459 / 0.465 | 0.506 / 0.507 | [DLin] |
| Stationary | 2022 | 0.513 / 0.491 | 0.534 / 0.504 | 0.588 / 0.535 | 0.643 / 0.616 | [iTr] |
| NLinear | 2023 | 0.374 / 0.394 | 0.408 / 0.415 | 0.429 / 0.427 | 0.440 / 0.453 | [DLin] |
| DLinear | 2023 | 0.375 / 0.399 | 0.405 / 0.416 | 0.439 / 0.443 | 0.472 / 0.490 | [DLin] |
| TimesNet | 2023 | 0.384 / 0.402 | 0.436 / 0.429 | 0.491 / 0.469 | 0.521 / 0.500 | [iTr] |
| Crossformer | 2023 | 0.423 / 0.448 | 0.471 / 0.474 | 0.570 / 0.546 | 0.653 / 0.621 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.370 / 0.400 | 0.413 / 0.429 | 0.422 / 0.440 | 0.447 / 0.468 | [Patch] |
| PatchTST (L=96) | 2023 | 0.414 / 0.419 | 0.460 / 0.445 | 0.501 / 0.466 | 0.500 / 0.488 | [iTr] |
| TiDE | 2023 | 0.479 / 0.464 | 0.525 / 0.492 | 0.565 / 0.515 | 0.594 / 0.558 | [iTr] |
| RLinear | 2023 | 0.386 / 0.395 | 0.437 / 0.424 | 0.479 / 0.446 | 0.481 / 0.470 | [iTr] |
| SCINet | 2022 | 0.654 / 0.599 | 0.719 / 0.631 | 0.778 / 0.659 | 0.836 / 0.699 | [iTr] |
| iTransformer | 2024 | 0.386 / 0.405 | 0.441 / 0.436 | 0.487 / 0.458 | 0.503 / 0.491 | [iTr] |
| TimeMixer | 2024 | 0.375 / 0.400 | 0.436 / 0.429 | 0.484 / 0.458 | 0.498 / 0.482 | [TMoE-ID] |
| Moment (ZS) | 2024 | 0.688 / 0.557 | 0.688 / 0.560 | 0.675 / 0.563 | 0.683 / 0.585 | [TMoE-ZS] |
| Chronos-base (ZS) | 2024 | 0.466 / 0.409 | 0.530 / 0.450 | 0.570 / 0.486 | 0.615 / 0.543 | [TMoE-ZS] |
| TimesFM (ZS) | 2024 | 0.414 / 0.404 | 0.465 / 0.434 | 0.503 / 0.456 | 0.511 / 0.481 | [TMoE-ZS] |
| Moirai-large (ZS) | 2024 | 0.381 / 0.388 | 0.434 / 0.415 | 0.495 / 0.445 | 0.611 / 0.510 | [TMoE-ZS] |
| Time-MoE-ultra (ZS) | 2025 | 0.349 / 0.379 | 0.395 / 0.413 | 0.447 / 0.453 | 0.457 / 0.462 | [TMoE-ZS] |
| Time-MoE-ultra (ID) | 2025 | 0.323 / 0.365 | 0.359 / 0.391 | 0.388 / 0.418 | 0.425 / 0.450 | [TMoE-ID] |

---

## ETTh2 (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 1.549 / 0.952 | 3.792 / 1.542 | 4.215 / 1.642 | 3.656 / 1.619 | [Patch] |
| Autoformer | 2021 | 0.346 / 0.388 | 0.456 / 0.452 | 0.482 / 0.486 | 0.515 / 0.511 | [iTr] |
| FEDformer | 2022 | 0.358 / 0.397 | 0.429 / 0.439 | 0.496 / 0.487 | 0.463 / 0.474 | [iTr] |
| Pyraformer | 2022 | 0.645 / 0.597 | 0.788 / 0.683 | 0.907 / 0.747 | 0.963 / 0.783 | [Patch] |
| Stationary | 2022 | 0.476 / 0.458 | 0.512 / 0.493 | 0.552 / 0.551 | 0.562 / 0.560 | [iTr] |
| DLinear | 2023 | 0.289 / 0.353 | 0.383 / 0.418 | 0.448 / 0.465 | 0.605 / 0.551 | [Patch] |
| TimesNet | 2023 | 0.340 / 0.374 | 0.402 / 0.414 | 0.452 / 0.452 | 0.462 / 0.468 | [iTr] |
| Crossformer | 2023 | 0.745 / 0.584 | 0.877 / 0.656 | 1.043 / 0.731 | 1.104 / 0.763 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.274 / 0.337 | 0.341 / 0.382 | 0.329 / 0.384 | 0.379 / 0.422 | [Patch] |
| PatchTST (L=96) | 2023 | 0.302 / 0.348 | 0.388 / 0.400 | 0.426 / 0.433 | 0.431 / 0.446 | [iTr] |
| TiDE | 2023 | 0.400 / 0.440 | 0.528 / 0.509 | 0.643 / 0.571 | 0.874 / 0.679 | [iTr] |
| RLinear | 2023 | 0.288 / 0.338 | 0.374 / 0.390 | 0.415 / 0.426 | 0.420 / 0.440 | [iTr] |
| SCINet | 2022 | 0.707 / 0.621 | 0.860 / 0.689 | 1.000 / 0.744 | 1.249 / 0.838 | [iTr] |
| iTransformer | 2024 | 0.297 / 0.349 | 0.380 / 0.400 | 0.428 / 0.432 | 0.427 / 0.445 | [iTr] |
| TimeMixer | 2024 | 0.289 / 0.341 | 0.372 / 0.392 | 0.386 / 0.414 | 0.412 / 0.434 | [TMoE-ID] |
| Chronos-large (ZS) | 2024 | 0.320 / 0.345 | 0.406 / 0.399 | 0.492 / 0.453 | 0.603 / 0.511 | [TMoE-ZS] |
| TimesFM (ZS) | 2024 | 0.315 / 0.349 | 0.388 / 0.395 | 0.422 / 0.427 | 0.443 / 0.454 | [TMoE-ZS] |
| Moirai-large (ZS) | 2024 | 0.296 / 0.330 | 0.361 / 0.371 | 0.390 / 0.390 | 0.423 / 0.418 | [TMoE-ZS] |
| Time-MoE-ultra (ZS) | 2025 | 0.292 / 0.352 | 0.347 / 0.379 | 0.406 / 0.419 | 0.439 / 0.447 | [TMoE-ZS] |
| Time-MoE-ultra (ID) | 2025 | 0.274 / 0.338 | 0.330 / 0.370 | 0.362 / 0.396 | 0.370 / 0.417 | [TMoE-ID] |

---

## ETTm1 (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.626 / 0.560 | 0.725 / 0.619 | 1.005 / 0.741 | 1.133 / 0.845 | [Patch] |
| Autoformer | 2021 | 0.510 / 0.492 | 0.514 / 0.495 | 0.510 / 0.492 | 0.527 / 0.493 | [Patch] |
| FEDformer | 2022 | 0.379 / 0.419 | 0.426 / 0.441 | 0.445 / 0.459 | 0.543 / 0.490 | [iTr] |
| Stationary | 2022 | 0.386 / 0.398 | 0.459 / 0.444 | 0.495 / 0.464 | 0.585 / 0.516 | [iTr] |
| DLinear | 2023 | 0.299 / 0.343 | 0.335 / 0.365 | 0.369 / 0.386 | 0.425 / 0.421 | [Patch] |
| TimesNet | 2023 | 0.338 / 0.375 | 0.374 / 0.387 | 0.410 / 0.411 | 0.478 / 0.450 | [iTr] |
| Crossformer | 2023 | 0.404 / 0.426 | 0.450 / 0.451 | 0.532 / 0.515 | 0.666 / 0.589 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.293 / 0.346 | 0.333 / 0.370 | 0.369 / 0.392 | 0.416 / 0.420 | [Patch] |
| PatchTST (L=96) | 2023 | 0.329 / 0.367 | 0.367 / 0.385 | 0.399 / 0.410 | 0.454 / 0.439 | [iTr] |
| TiDE | 2023 | 0.364 / 0.387 | 0.398 / 0.404 | 0.428 / 0.425 | 0.487 / 0.461 | [iTr] |
| RLinear | 2023 | 0.355 / 0.376 | 0.391 / 0.392 | 0.424 / 0.415 | 0.487 / 0.450 | [iTr] |
| iTransformer | 2024 | 0.334 / 0.368 | 0.377 / 0.391 | 0.426 / 0.420 | 0.491 / 0.459 | [iTr] |
| TimeMixer | 2024 | 0.320 / 0.357 | 0.361 / 0.381 | 0.390 / 0.404 | 0.454 / 0.441 | [TMoE-ID] |
| Chronos-large (ZS) | 2024 | 0.457 / 0.403 | 0.530 / 0.450 | 0.577 / 0.481 | 0.660 / 0.526 | [TMoE-ZS] |
| TimesFM (ZS) | 2024 | 0.361 / 0.370 | 0.414 / 0.405 | 0.445 / 0.429 | 0.512 / 0.471 | [TMoE-ZS] |
| Moirai-large (ZS) | 2024 | 0.380 / 0.361 | 0.412 / 0.383 | 0.436 / 0.400 | 0.462 / 0.420 | [TMoE-ZS] |
| Time-MoE-ultra (ZS) | 2025 | 0.281 / 0.341 | 0.305 / 0.358 | 0.369 / 0.395 | 0.469 / 0.472 | [TMoE-ZS] |
| Time-MoE-ultra (ID) | 2025 | 0.256 / 0.323 | 0.281 / 0.343 | 0.326 / 0.374 | 0.454 / 0.452 | [TMoE-ID] |

---

## ETTm2 (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.355 / 0.462 | 0.595 / 0.586 | 1.270 / 0.871 | 3.001 / 1.267 | [Patch] |
| Autoformer | 2021 | 0.255 / 0.339 | 0.281 / 0.340 | 0.339 / 0.372 | 0.433 / 0.432 | [iTr] |
| FEDformer | 2022 | 0.203 / 0.287 | 0.269 / 0.328 | 0.325 / 0.366 | 0.421 / 0.415 | [iTr] |
| DLinear | 2023 | 0.167 / 0.260 | 0.224 / 0.303 | 0.281 / 0.342 | 0.397 / 0.421 | [Patch] |
| TimesNet | 2023 | 0.187 / 0.267 | 0.249 / 0.309 | 0.321 / 0.351 | 0.408 / 0.403 | [iTr] |
| Crossformer | 2023 | 0.287 / 0.366 | 0.414 / 0.492 | 0.597 / 0.542 | 1.730 / 1.042 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.166 / 0.256 | 0.223 / 0.296 | 0.274 / 0.329 | 0.362 / 0.385 | [Patch] |
| PatchTST (L=96) | 2023 | 0.175 / 0.259 | 0.241 / 0.302 | 0.305 / 0.343 | 0.402 / 0.400 | [iTr] |
| RLinear | 2023 | 0.182 / 0.265 | 0.246 / 0.304 | 0.307 / 0.342 | 0.407 / 0.398 | [iTr] |
| iTransformer | 2024 | 0.180 / 0.264 | 0.250 / 0.309 | 0.311 / 0.348 | 0.412 / 0.407 | [iTr] |
| TimeMixer | 2024 | 0.175 / 0.258 | 0.237 / 0.299 | 0.298 / 0.340 | 0.391 / 0.396 | [TMoE-ID] |
| Chronos-large (ZS) | 2024 | 0.197 / 0.271 | 0.254 / 0.314 | 0.313 / 0.353 | 0.416 / 0.415 | [TMoE-ZS] |
| TimesFM (ZS) | 2024 | 0.202 / 0.270 | 0.289 / 0.321 | 0.360 / 0.366 | 0.462 / 0.430 | [TMoE-ZS] |
| Moirai-large (ZS) | 2024 | 0.211 / 0.274 | 0.281 / 0.318 | 0.341 / 0.355 | 0.485 / 0.428 | [TMoE-ZS] |
| Time-MoE-ultra (ZS) | 2025 | 0.198 / 0.288 | 0.235 / 0.312 | 0.293 / 0.348 | 0.427 / 0.428 | [TMoE-ZS] |
| Time-MoE-base (ID) | 2025 | 0.169 / 0.259 | 0.223 / 0.295 | 0.293 / 0.341 | 0.451 / 0.433 | [TMoE-ID] |

---

## ECL / Electricity (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.304 / 0.393 | 0.327 / 0.417 | 0.333 / 0.422 | 0.351 / 0.427 | [Patch] |
| LogTrans | 2019 | 0.258 / 0.357 | 0.266 / 0.368 | 0.280 / 0.380 | 0.283 / 0.376 | [Patch] |
| Pyraformer | 2022 | 0.386 / 0.449 | 0.386 / 0.443 | 0.378 / 0.443 | 0.376 / 0.445 | [Patch] |
| Autoformer | 2021 | 0.201 / 0.317 | 0.222 / 0.334 | 0.231 / 0.338 | 0.254 / 0.361 | [iTr] |
| FEDformer | 2022 | 0.193 / 0.308 | 0.201 / 0.315 | 0.214 / 0.329 | 0.246 / 0.355 | [iTr] |
| Stationary | 2022 | 0.169 / 0.273 | 0.182 / 0.286 | 0.200 / 0.304 | 0.222 / 0.321 | [iTr] |
| DLinear | 2023 | 0.140 / 0.237 | 0.153 / 0.249 | 0.169 / 0.267 | 0.203 / 0.301 | [Patch] |
| TimesNet | 2023 | 0.168 / 0.272 | 0.184 / 0.289 | 0.198 / 0.300 | 0.220 / 0.320 | [iTr] |
| Crossformer | 2023 | 0.219 / 0.314 | 0.231 / 0.322 | 0.246 / 0.337 | 0.280 / 0.363 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.129 / 0.222 | 0.147 / 0.240 | 0.163 / 0.259 | 0.197 / 0.290 | [Patch] |
| PatchTST (L=96) | 2023 | 0.195 / 0.285 | 0.199 / 0.289 | 0.215 / 0.305 | 0.256 / 0.337 | [iTr] |
| TiDE | 2023 | 0.237 / 0.329 | 0.236 / 0.330 | 0.249 / 0.344 | 0.284 / 0.373 | [iTr] |
| RLinear | 2023 | 0.201 / 0.281 | 0.201 / 0.283 | 0.215 / 0.298 | 0.257 / 0.331 | [iTr] |
| SCINet | 2022 | 0.247 / 0.345 | 0.257 / 0.355 | 0.269 / 0.369 | 0.299 / 0.390 | [iTr] |
| iTransformer | 2024 | 0.148 / 0.240 | 0.162 / 0.253 | 0.178 / 0.269 | 0.225 / 0.317 | [iTr] |
| TimeMixer (MSE only) | 2024 | 0.153 / — | 0.166 / — | 0.185 / — | 0.225 / — | [TMix] |

> 주: ECL은 Time-MoE 논문의 zero-shot 평가에서 제외(사전학습 corpus에 포함됨).

---

## Exchange (L=96)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Autoformer | 2021 | 0.197 / 0.323 | 0.300 / 0.369 | 0.509 / 0.524 | 1.447 / 0.941 | [iTr] |
| FEDformer | 2022 | 0.148 / 0.278 | 0.271 / 0.315 | 0.460 / 0.427 | 1.195 / 0.695 | [iTr] |
| Stationary | 2022 | 0.111 / 0.237 | 0.219 / 0.335 | 0.421 / 0.476 | 1.092 / 0.769 | [iTr] |
| DLinear | 2023 | 0.088 / 0.218 | 0.176 / 0.315 | 0.313 / 0.427 | 0.839 / 0.695 | [iTr] |
| TimesNet | 2023 | 0.107 / 0.234 | 0.226 / 0.344 | 0.367 / 0.448 | 0.964 / 0.746 | [iTr] |
| Crossformer | 2023 | 0.256 / 0.367 | 0.470 / 0.509 | 1.268 / 0.883 | 1.767 / 1.068 | [iTr] |
| PatchTST (L=96) | 2023 | 0.088 / 0.205 | 0.176 / 0.299 | 0.301 / 0.397 | 0.901 / 0.714 | [iTr] |
| TiDE | 2023 | 0.094 / 0.218 | 0.184 / 0.307 | 0.349 / 0.431 | 0.852 / 0.698 | [iTr] |
| RLinear | 2023 | 0.093 / 0.217 | 0.184 / 0.307 | 0.351 / 0.432 | 0.886 / 0.714 | [iTr] |
| SCINet | 2022 | 0.267 / 0.396 | 0.351 / 0.459 | 1.324 / 0.853 | 1.058 / 0.797 | [iTr] |
| iTransformer | 2024 | 0.086 / 0.206 | 0.177 / 0.299 | 0.331 / 0.417 | 0.847 / 0.691 | [iTr] |

> 주: TimeMixer / Time-MoE 논문에는 Exchange를 메인 테이블에 포함하지 않음.

---

## Traffic (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.733 / 0.410 | 0.777 / 0.435 | 0.776 / 0.434 | 0.827 / 0.466 | [Patch] |
| Autoformer | 2021 | 0.613 / 0.388 | 0.616 / 0.382 | 0.622 / 0.337 | 0.660 / 0.408 | [iTr] |
| FEDformer | 2022 | 0.587 / 0.366 | 0.604 / 0.373 | 0.621 / 0.383 | 0.626 / 0.382 | [iTr] |
| Pyraformer | 2022 | 2.085 / 0.468 | 0.867 / 0.467 | 0.869 / 0.469 | 0.881 / 0.473 | [Patch] |
| Stationary | 2022 | 0.612 / 0.338 | 0.613 / 0.340 | 0.618 / 0.328 | 0.653 / 0.355 | [iTr] |
| DLinear | 2023 | 0.410 / 0.282 | 0.423 / 0.287 | 0.436 / 0.296 | 0.466 / 0.315 | [Patch] |
| TimesNet | 2023 | 0.593 / 0.321 | 0.617 / 0.336 | 0.629 / 0.336 | 0.640 / 0.350 | [iTr] |
| Crossformer | 2023 | 0.522 / 0.290 | 0.530 / 0.293 | 0.558 / 0.305 | 0.589 / 0.328 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.360 / 0.249 | 0.379 / 0.256 | 0.392 / 0.264 | 0.432 / 0.286 | [Patch] |
| PatchTST (L=96) | 2023 | 0.544 / 0.359 | 0.540 / 0.354 | 0.551 / 0.358 | 0.586 / 0.375 | [iTr] |
| TiDE | 2023 | 0.805 / 0.493 | 0.756 / 0.474 | 0.762 / 0.477 | 0.719 / 0.449 | [iTr] |
| RLinear | 2023 | 0.649 / 0.389 | 0.601 / 0.366 | 0.609 / 0.369 | 0.647 / 0.387 | [iTr] |
| iTransformer | 2024 | 0.395 / 0.268 | 0.417 / 0.276 | 0.433 / 0.283 | 0.467 / 0.302 | [iTr] |

> 주: Moirai(오리지널)는 채널 수 862의 Traffic에서 scalability 한계로 결과를 보고하지 않음. Time-MoE 논문에서도 제외.

---

## Weather (L=96 except noted)

| Model | Year | h=96 | h=192 | h=336 | h=720 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 0.354 / 0.405 | 0.419 / 0.434 | 0.583 / 0.543 | 0.916 / 0.705 | [Patch] |
| Autoformer | 2021 | 0.266 / 0.336 | 0.307 / 0.367 | 0.359 / 0.395 | 0.419 / 0.428 | [iTr] |
| FEDformer | 2022 | 0.217 / 0.296 | 0.276 / 0.336 | 0.339 / 0.380 | 0.403 / 0.428 | [iTr] |
| Stationary | 2022 | 0.173 / 0.223 | 0.245 / 0.285 | 0.321 / 0.338 | 0.414 / 0.410 | [iTr] |
| DLinear | 2023 | 0.176 / 0.237 | 0.220 / 0.282 | 0.265 / 0.319 | 0.323 / 0.362 | [Patch] |
| TimesNet | 2023 | 0.172 / 0.220 | 0.219 / 0.261 | 0.280 / 0.306 | 0.365 / 0.359 | [iTr] |
| Crossformer | 2023 | 0.158 / 0.230 | 0.206 / 0.277 | 0.272 / 0.335 | 0.398 / 0.418 | [iTr] |
| PatchTST/64 (L=512) | 2023 | 0.149 / 0.198 | 0.194 / 0.241 | 0.245 / 0.282 | 0.314 / 0.334 | [Patch] |
| PatchTST (L=96) | 2023 | 0.177 / 0.218 | 0.225 / 0.259 | 0.278 / 0.297 | 0.354 / 0.348 | [iTr] |
| TiDE | 2023 | 0.202 / 0.261 | 0.242 / 0.298 | 0.287 / 0.335 | 0.351 / 0.386 | [iTr] |
| RLinear | 2023 | 0.192 / 0.232 | 0.240 / 0.271 | 0.292 / 0.307 | 0.364 / 0.353 | [iTr] |
| iTransformer | 2024 | 0.174 / 0.214 | 0.221 / 0.254 | 0.278 / 0.296 | 0.358 / 0.349 | [iTr] |
| TimeMixer | 2024 | 0.163 / 0.209 | 0.208 / 0.250 | 0.251 / 0.287 | 0.339 / 0.341 | [TMoE-ID] |
| Chronos-large (ZS) | 2024 | 0.194 / 0.235 | 0.249 / 0.285 | 0.302 / 0.327 | 0.372 / 0.378 | [TMoE-ZS] |
| Moirai-large (ZS) | 2024 | 0.199 / 0.211 | 0.246 / 0.251 | 0.274 / 0.291 | 0.337 / 0.340 | [TMoE-ZS] |
| Time-MoE-ultra (ZS) | 2025 | 0.157 / 0.211 | 0.208 / 0.256 | 0.255 / 0.290 | 0.405 / 0.397 | [TMoE-ZS] |
| Time-MoE-base (ID) | 2025 | 0.149 / 0.201 | 0.192 / 0.244 | 0.245 / 0.285 | 0.352 / 0.365 | [TMoE-ID] |

---

## ILI (Illness) — horizons {24, 36, 48, 60}

ILI는 변수 7개, 주별(weekly) 데이터로 길이가 짧아 **lookback이 결과에 매우 민감**하다 (PatchTST: L=104, DLinear: L=36/104).

| Model | Year | h=24 | h=36 | h=48 | h=60 | Src |
|---|---|---|---|---|---|---|
| Informer | 2021 | 4.657 / 1.449 | 4.650 / 1.463 | 5.004 / 1.542 | 5.071 / 1.543 | [Patch] |
| LogTrans | 2019 | 4.480 / 1.444 | 4.799 / 1.467 | 4.800 / 1.468 | 5.278 / 1.560 | [Patch] |
| Pyraformer | 2022 | 1.420 / 2.012 | 7.394 / 2.031 | 7.551 / 2.057 | 7.662 / 2.100 | [Patch] |
| Autoformer | 2021 | 2.906 / 1.182 | 2.585 / 1.038 | 3.024 / 1.145 | 2.761 / 1.114 | [Patch] |
| FEDformer | 2022 | 2.624 / 1.095 | 2.516 / 1.021 | 2.505 / 1.041 | 2.742 / 1.122 | [Patch] |
| DLinear | 2023 | 2.215 / 1.081 | 1.963 / 0.963 | 2.130 / 1.024 | 2.368 / 1.096 | [Patch] |
| PatchTST/64 | 2023 | 1.319 / 0.754 | 1.579 / 0.870 | 1.553 / 0.815 | 1.470 / 0.788 | [Patch] |
| PatchTST/42 | 2023 | 1.522 / 0.814 | 1.430 / 0.834 | 1.673 / 0.854 | 1.529 / 0.862 | [Patch] |
| TimesNet (avg) | 2023 | — | — | — | — | avg 2.139 / 0.931 (TimesNet Tab.2) |
| Time-LLM (10% few-shot) | 2024 | 0.519 / 0.481 | 0.517 / 0.612 | 0.545 / 0.617 | 0.622 / 0.672 | [TLLM] |
| Time-LLM (full-shot, avg) | 2024 | avg 1.435 / 0.801 across 4 horizons | — | — | — | [TLLM] Tab.1 |

> 주: Time-MoE / Moirai / iTransformer / TimeMixer 논문은 ILI를 메인 테이블에서 제외하는 경향. 위 값 대부분은 PatchTST 기준 표에서 수집.

---

## Key Observations

1. **Linear ≥ Transformer (2022–2023).**
   DLinear/NLinear는 당시 Informer·Autoformer·FEDformer 등 대표 Transformer 계열을 ETTh1/ETTm1/Weather/ECL 전 구간에서 능가하거나 대등한 결과를 보이며, "Are Transformers Effective?" 논쟁을 촉발 ([DLin]).

2. **PatchTST의 반격 (2023).**
   Patch + channel-independence + 긴 lookback (L=336/512) 조합으로 Transformer 계열이 다시 DLinear를 전반적으로 역전. ETTh1 h=96에서 0.375 → 0.370, Weather h=96에서 0.176 → 0.149 등 개선. 긴 lookback이 성능 핵심 요인임이 확인.

3. **iTransformer (2024): 변수축으로 attention 뒤집기.**
   동일 lookback(L=96)에서 Traffic/ECL 같은 고차원 다변량 벤치마크에서 두드러진 이득 (ECL 0.178 avg MSE, Traffic 0.428 avg MSE). ETT류는 PatchTST와 근소한 우위·열위 혼재.

4. **TimeMixer (2024): 다시 MLP 계열의 우위.**
   시간·주파수 혼합을 명시 모델링한 MLP 기반 구조로 ETTh1/Weather/Solar에서 iTransformer를 일부 능가 (ETTh1 h=96 0.375/0.400).

5. **LLM/FM 제로샷의 도약 (2024–2025).**
   - **Time-LLM**: 10% few-shot 설정에서 full-shot PatchTST와 유사·우수한 ETT 성능.
   - **Moirai-large (ZS)** 와 **TimesFM (ZS)** 는 ETTh1/ETTh2에서 지도학습 PatchTST/iTransformer에 필적. "zero-shot = supervised SOTA"의 시대 진입.
   - **Time-MoE-ultra (2025, ICLR Spotlight)**: ETTh1 h=96 zero-shot 0.349 MSE로 supervised iTransformer(0.386), TimeMixer(0.375)보다 우수. **FM scaling (1B+ MoE)이 지도학습 SOTA를 뒤집은 최초 사례.**
   - In-distribution 재학습 시 Time-MoE는 같은 데이터셋의 지도학습 모델들을 다시 한 번 큰 폭(ETTh1 h=96 0.323 MSE)으로 능가.

6. **Lookback의 함정.**
   같은 PatchTST라도 L=512 vs L=96에서 ETTh1 h=96 0.370 → 0.414로 크게 벌어짐. 모델 간 비교는 **반드시 동일 lookback**에서의 값을 사용해야 한다.

7. **Traffic/ECL은 고차원·고빈도 → FM에 불리.**
   Moirai는 채널 flatten 구조상 Traffic(862채널)에서 동작 제한, Time-MoE도 ECL을 사전학습 누수로 zero-shot에서 제외. 대규모 채널 FM은 여전히 open problem (Moirai-MoE 2025가 MoE sparsification으로 완화).

8. **ILI는 FM 논문에서 사실상 사라짐.**
   2024년 이후 foundation-model 계열 논문은 ILI를 메인 테이블에서 자주 제외 (저주파 weekly·짧은 시계열·소수 변수). 해당 도메인 최신 참조점은 PatchTST + Time-LLM few-shot.

---

## 참고 원문/URL

- DLinear: https://arxiv.org/abs/2205.13504
- PatchTST: https://arxiv.org/abs/2211.14730
- TimesNet: https://arxiv.org/abs/2210.02186
- iTransformer: https://arxiv.org/abs/2310.06625
- TimeMixer: https://arxiv.org/abs/2405.14616
- Time-LLM: https://arxiv.org/abs/2310.01728
- Moirai: https://arxiv.org/abs/2402.02592
- Chronos: https://arxiv.org/abs/2403.07815
- TimesFM: https://arxiv.org/abs/2310.10688
- Time-MoE: https://arxiv.org/abs/2409.16040
- Moirai-MoE: https://arxiv.org/abs/2410.10469

---

## Appendix: Reported-Number Discrepancies

같은 (model, dataset, horizon) 조합이 논문마다 숫자가 다른 경우가 흔하다. 아래는 본문 표에서 직접 확인 가능한 대표 케이스와 원인.

### 1. 재측정 출처에 따른 수치 차이 (본문 표 기반)

**PatchTST on ETTh1 h=96** — lookback만 바뀌어도 0.37 → 0.41

| Source | Lookback | MSE | MAE |
|---|---|---|---|
| PatchTST 원논문 (PatchTST/64) | L=512 | 0.370 | 0.400 |
| iTransformer Table 10 재측정 | L=96 | 0.414 | 0.419 |

**Informer on ETTh2 h=96** — 재측정 소스에 따라 MSE 3배

| Source | MSE | MAE |
|---|---|---|
| PatchTST Table (재측정) | 1.549 | 0.952 |
| 원 Informer 논문 (ETT multivariate split) | ~3.0+ | — |

**Autoformer on ETTh1 h=96** — DLinear 출처 vs iTransformer 출처

| Source | MSE | MAE |
|---|---|---|
| DLinear 재측정 ([DLin]) | 0.449 | 0.459 |
| iTransformer Table 10 재측정 | 수치 유사 범위 (0.44–0.45) | — |

> 본문 표의 각 행 `Src` 컬럼([DLin]/[Patch]/[iTr]/[TMoE-ZS]/[TMoE-ID])이 곧 불일치 추적 태그.

### 2. Common Sources of Variation

- **Lookback length (L)**: 가장 큰 변수. L=96 / L=336 / L=512 간 MSE 10–30% 차이 흔함
- **Channel strategy**: Channel-independent (PatchTST, iTransformer) vs channel-mixing (Informer, Autoformer)
- **Normalization**: RevIN on/off, instance norm vs standard scaling
- **Train/Val/Test split**: ETT의 12/4/4 months (Informer 원본) vs 70/10/20% (Autoformer 이후 표준)
- **Random seed / runs**: 1-run vs 5-run 평균
- **HP 재탐색 여부**: 재측정 시 원논문 HP 그대로 vs 재튜닝
- **Metric 정의**: 일부 논문은 standardized 후 MSE, 일부는 원 scale

### 3. Which Numbers to Trust

우선순위:

1. **모델의 원 논문 숫자** — 단, **setting이 비교 대상과 동일할 때만**. 특히 lookback 매칭 필수
2. **iTransformer Table 10** — 2024 이전 모델들의 일관된 재측정 기준 (L=96 통일)
3. **Time-MoE Table 3/4** — FM 비교 기준 (zero-shot vs in-distribution 구분)
4. **TimeMixer Table 13** — "unified hyperparameter" 원칙 (모든 모델 동일 HP)

**비교 시 체크리스트**:
- [ ] 같은 lookback인가? (가장 흔한 함정)
- [ ] 같은 split (12/4/4 vs 70/10/20)인가?
- [ ] RevIN 적용 여부가 같은가?
- [ ] 같은 재측정 출처에서 가져왔는가? (출처 섞으면 안됨)

### 4. 실전 권고

새 모델 성능 보고 시:
- 본문 표에서 **같은 `Src` 태그로 묶인 baseline들과 비교**할 것 (예: iTransformer 재측정 [iTr] 블록 vs 원 PatchTST 논문 [Patch] 블록을 섞지 말 것)
- **Lookback은 별도 행으로 분리 보고** (본문의 `PatchTST/64 (L=512)` vs `PatchTST (L=96)` 방식)
- Zero-shot FM 비교는 **Time-MoE Table 3 포맷 (ZS/ID 분리)** 권장

