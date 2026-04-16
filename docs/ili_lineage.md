# ILI Forecasting Model Lineage (2018–2026)

ILI (Influenza-Like Illness) 특화 딥러닝 예측 모델 계보. 일반 LTSF 모델(Informer/PatchTST/DLinear 등)은 제외. **[verified]** = 원 논문 확인, **[unverified]** = 2차 자료 기반.

---

## 1. 연대표

| Year | Model          | Paper                                                                                                 | Venue                 | arXiv / DOI                                                       |
|------|----------------|-------------------------------------------------------------------------------------------------------|-----------------------|-------------------------------------------------------------------|
| 2015 | ARGO           | Accurate estimation of influenza epidemics using Google search data via ARGO                          | PNAS                  | 10.1073/pnas.1515373112                                           |
| 2018 | CNNRNN-Res     | Deep Learning for Epidemiological Predictions (Wu et al.)                                             | SIGIR 2018            | 10.1145/3209978.3210077                                           |
| 2019 | ARGONet        | Improved state-level influenza nowcasting leveraging Internet data and network approaches             | Nature Communications | 10.1038/s41467-018-08082-0                                        |
| 2019 | EpiDeep        | EpiDeep: Exploiting Embeddings for Epidemic Forecasting (Adhikari et al.)                             | KDD 2019              | 10.1145/3292500.3330917                                           |
| 2019 | Attention-RNN  | Attention-based RNN for influenza epidemic prediction (Zhu et al.)                                    | BMC Bioinformatics    | 10.1186/s12859-019-3131-8                                         |
| 2020 | Cola-GNN       | Cola-GNN: Cross-location Attention based GNN for Long-term ILI Prediction (Deng et al.)               | CIKM 2020             | 10.1145/3340531.3411975                                           |
| 2021 | CALI-Net       | CALI-Net: Calibrated Epidemiological Forecasting with Regime-Shift Awareness                          | AAAI 2021             | (Kamarthi et al.)                                                 |
| 2021 | DeepGLEAM      | DeepGLEAM: Hybrid Mechanistic and Deep Learning Model for COVID-19 Forecasting (Wu/Chinazzi et al.)   | arXiv / AAAI-W        | arXiv:2102.06684                                                  |
| 2022 | EpiGNN         | EpiGNN: Exploring Spatial Transmission with GNN for Regional Epidemic Forecasting (Xie et al.)        | ECML-PKDD 2022        | arXiv:2208.11517                                                  |
| 2022 | SAIFlu-Net     | Self-attention + LSTM for regional influenza forecasting (US/Japan) [unverified venue]                | (journal)             | (DOI TBD)                                                         |
| 2023 | RESEAT         | RESEAT: Recurrent Self-Attention Network for Multi-Regional Influenza Forecasting                     | IEEE Access           | IEEE Xplore doc 10050036                                          |
| 2024 | MPSTAN         | MPSTAN: Metapopulation-Based Spatio-Temporal Attention Network for Epidemic Forecasting               | Entropy (MDPI)        | arXiv:2306.12436 / 10.3390/e26040278                              |
| 2024 | EINN           | Epidemiology-informed GNN for Heterogeneity-aware Epidemic Forecasting                                | arXiv                 | arXiv:2411.17372                                                  |
| 2025 | FaXNet         | FaXNet: Frequency-adaptive, explainable, uncertainty-aware network for influenza forecasting          | Frontiers Public H.   | 10.3389/fpubh.2026.1746529                                        |
| 2025 | Relief         | Relief: regional interpretable ILI forecasting [unverified]                                           | (TBD)                 | (TBD)                                                             |

---

## 2. 계보 다이어그램 (ASCII)

굵은 계보(main trunk)는 `═>`, 곁가지(side branch)는 `->`. 도메인 교차는 `(xfer)`.

```
    ARGO (2015, Google search + AR)
       └─> ARGONet (2019, ARGO + network synchrony)

    CNNRNN (일반 multivariate TS)
       ║  (Wu et al. 2018, SIGIR)
       ▼
    CNNRNN-Res (2018) ══════════════════════════════════════ [ILI DL trunk]
       ║
       ├─> EpiDeep (2019, KDD) — curve-embedding branch, peak/onset targets
       │      └─> CALI-Net (2021, AAAI) — regime-shift (COVID) 대응
       ║
       ║   (Transformer attention → ILI, xfer)
       ▼
    Cola-GNN (2020, CIKM) ═════════════════════════ [spatio-temporal GNN trunk]
       │    : location-aware attention + graph message passing
       │
       ├─> EpiGNN (2022) — transmission-risk encoding, Region-Aware Graph Learner
       │      └─> EINN (2024) — epidemiology-informed / heterogeneity-aware
       │
       ├─> SAIFlu-Net (2022) — self-attention inter-region similarity + LSTM
       │      └─> RESEAT (2023) — *recurrent* self-attention (time-varying attn)
       │             └─> Relief (2025, unverified) — interpretable region branch
       │
       └─> MPSTAN (2024) — metapopulation SIR + spatio-temporal attn
              ├─ inspired by: DeepGLEAM (2021, mechanistic+DL)
              └─ inspired by: CausalGNN (2022)

    (xfer) Transformer (Vaswani 2017)
              └─> Attention-RNN for Flu (Zhu 2019)
              └─> Deep Transformer for ILI (Wu 2020, inspired)
              └─> FaXNet (2025) — frequency-adaptive + SHAP + probabilistic

    (xfer) Mechanistic GLEAM (Chinazzi)
              └─> DeepGLEAM (2021) — correction-term DL on top of GLEAM
                     └─> MPSTAN (2024, metapopulation SIR)
```

**핵심 분기**:
1. Pure DL trunk: CNNRNN-Res → Cola-GNN → EpiGNN / SAIFlu-Net → RESEAT / MPSTAN
2. Embedding / curve-matching branch: EpiDeep → CALI-Net
3. Hybrid mechanistic-DL: DeepGLEAM → MPSTAN
4. Explainability / Uncertainty: FaXNet, Relief, LLM+리포트 계열 (본 repo)

---

## 3. 모델별 상세

### CNNRNN-Res (2018, SIGIR)
- **Paper**: Wu, Yang, Nishiura, Saitoh. *Deep Learning for Epidemiological Predictions*. ([DOI](https://doi.org/10.1145/3209978.3210077))
- **핵심 아이디어**: CNN + RNN + residual을 결합해 다지역 ILI의 공간-시간 의존성을 end-to-end 학습. 기계론적 SIR 계열을 넘은 첫 ILI DL baseline. **[verified]**
- **구조**: input (regions × time) → CNN (cross-sectional fusion) → GRU (temporal) → residual skip → linear head.
- **강점**: AR/GP 대비 장기 horizon(≥10주) 개선; Japan 47 prefectures 등 many-region에서 확장성.
- **약점**: 지역 연결을 고정 conv kernel로 가정 — 실제 mobility/adjacency 반영 불가 (Cola-GNN의 주요 지적). Peak/onset 별도 target 부재.
- **계승**: Cola-GNN, SAIFlu-Net, EpiGNN의 공통 주요 baseline.
- **주요 숫자**: Japan/US 벤치에서 Cola-GNN 대비 RMSE 20–30% 높음(즉 열위) — **unverified exact**.

### EpiDeep (2019, KDD)
- **Paper**: Adhikari, Xu, Ramakrishnan, Prakash. ([PDF](https://people.cs.vt.edu/ramakris/papers/EpiDeepKDD2019.pdf))
- **핵심 아이디어**: 시즌별 incidence curve를 연속 임베딩 공간에 매핑 후, 현재 partial curve와 유사한 historical season을 retrieval해 incidence/peak intensity/peak time/onset을 동시 예측. **[verified]**
- **구조**: curve encoder → attention over past seasons → multi-head decoder(incidence + peak + onset).
- **강점**: 비자명 baseline 대비 최대 40% 개선 (US ILI, 저자 주장). Retrieval 기반 해석 가능성.
- **약점**: multi-region 공간 의존성 거의 없음(region별 학습). Regime shift(COVID)에서 급락 — CALI-Net(AAAI-21)이 후속 보완.
- **계승**: CALI-Net; retrieval 아이디어는 최근 LLM 기반 ICL ILI 예측(본 repo)에 영감.

### Cola-GNN (2020, CIKM)
- **Paper**: Deng, Wang, Rangwala 등. ([DOI](https://doi.org/10.1145/3340531.3411975))
- **핵심 아이디어**: 지역별 RNN 임베딩 + **location-aware cross-attention**으로 동적 adjacency 학습, 이후 graph message passing으로 장기 예측 강화. **[verified]**
- **구조**: per-location dilated-conv + RNN → location-aware attention(A_ij) → multi-layer GNN → MLP multi-horizon head.
- **강점**: 장기 horizon(h=15)에서 CNNRNN-Res 대비 RMSE/PCC 크게 개선. Japan-Prefectures(47), US-Regions(10), US-States(49)에서 일관된 우위.
- **약점**: attention을 window당 1회 계산 → 시간 내 동적 변화 미반영(RESEAT의 지적). 외부 변수(mobility/search/weather) 부재.
- **계승**: EpiGNN, SAIFlu-Net, RESEAT, MPSTAN 모두 직접 baseline.
- **주요 숫자**: Japan h=15에서 PCC ≈ 0.75–0.80 수준으로 보고(원 논문 Table 3) — **unverified exact**.

### EpiGNN (2022, ECML-PKDD)
- **Paper**: ([arXiv:2208.11517](https://arxiv.org/abs/2208.11517))
- **핵심 아이디어**: Cola-GNN 확장. Transmission risk encoding(local/global) + Region-Aware Graph Learner(RAGL, learnable adjacency + geographical prior). mobility 등 외부 결합 가능. **[verified]**
- **강점**: 5개 influenza/COVID 데이터셋에서 Cola-GNN 상회. mobility 추가 시 추가 이득.
- **약점**: RAGL이 데이터 양에 민감; region 수가 매우 적으면 이득 제한적 — **unverified**.
- **계승**: EINN(2024) 등 COVID 후속 GNN 라인.

### SAIFlu-Net (2022)
- **핵심 아이디어**: per-region LSTM + **self-attention 기반 region 간 유사도** 추출로 수작업 그래프 불필요. **[unverified — venue 미확인]**
- **강점**: Cola-GNN/CNNRNN 대비 RMSE/PCC 개선(저자 주장, US/Japan).
- **약점**: 장기 horizon(h≥15) 성능 열화, 외부(weather/social) 미사용.
- **계승**: RESEAT가 "attention이 시간 고정"이라는 한계를 직접 지적·확장.

### RESEAT (2023, IEEE Access)
- **Paper**: *Recurrent Self-Attention Network for Multi-Regional Influenza Forecasting*. ([IEEE doc 10050036](https://ieeexplore.ieee.org/document/10050036/))
- **핵심 아이디어**: SAIFlu-Net/Cola-GNN의 "한 번 계산되는 attention" 한계를 지적, **매 time step마다 region 관계를 재계산**하는 recurrent self-attention 도입. **[verified (abstract)]**
- **구조**: per-time-step self-attention cell(recurrent) + GRU-like state → multi-region joint head.
- **강점**: 시즌 피크 전후 등 시간 내 역학 변동 포착. 다지역 joint 예측.
- **약점**: recurrent attention으로 계산량 증가. 외부 feature/텍스트 통합 부재.
- **계승**: 본 repo의 region-prompt 예측 및 Relief(2025) 방향.

### MPSTAN (2024, Entropy)
- **Paper**: ([arXiv:2306.12436](https://arxiv.org/abs/2306.12436))
- **핵심 아이디어**: metapopulation SIR 지식을 spatio-temporal attention과 결합; intra-/inter-patch 파라미터를 각각 학습하는 multi-parameter generator. **[verified]**
- **구조**: recurrent cell = {spatio-temporal, epidemiology(SIR), multi-param generator, fusion}.
- **강점**: 단/장기 모두 안정, regime shift 대응력 ↑(mechanistic anchor).
- **약점**: mobility 데이터 없으면 inter-patch param이 degenerate 위험; 검증 데이터셋 2개로 제한.
- **계승**: DeepGLEAM의 mechanistic+DL 라인을 메타개체군 수준으로 일반화.

### DeepGLEAM (2021)
- **Paper**: ([arXiv:2102.06684](https://arxiv.org/abs/2102.06684))
- **핵심 아이디어**: 대규모 stochastic simulation(GLEAM) 출력에 DL **bias-correction**. **[verified]**
- **강점**: 물리 일관성 + DL 보정 + 불확실성 정량화.
- **약점**: GLEAM 시뮬레이션 비용·재현성 이슈. COVID 특화로 ILI flu 벤치 비교 드뭄.
- **계승**: MPSTAN, EINN 등 hybrid mechanistic-DL의 원형.

### ARGO / ARGONet (2015 / 2019)
- **ARGO**: Yang, Santillana, Kou. PNAS 2015. ([DOI](https://doi.org/10.1073/pnas.1515373112))
- **ARGONet**: Lu, Hua, Santillana. Nat Commun 2019. ([DOI](https://doi.org/10.1038/s41467-018-08082-0))
- **핵심 아이디어**: Google search + EHR + historical ILI의 AR nowcasting (ARGO). ARGONet = ARGO + state-to-state network synchrony 앙상블.
- **강점**: 주(state) 수준 nowcasting에서 2014–2017 시즌 75%+ 주에서 ARGO 상회.
- **약점**: h=0 nowcast 중심; long-horizon 비대상. Search-query 편차 민감.
- **계승**: FaXNet의 "search trend + uncertainty" 라인에 영향.

### EINN (2024)
- ([arXiv:2411.17372](https://arxiv.org/abs/2411.17372))
- **핵심 아이디어**: 지역 이질성(demographics, 접종률 등)을 GNN에 주입 + epidemiological prior로 물리 일관성.
- **강점**: 이질성 큰 벤치(US state-level)에서 EpiGNN 대비 이득 보고 — **unverified exact**.
- **약점**: 이질성 feature가 풍부한 환경에 한정.

### FaXNet (2025, Frontiers Public Health)
- **핵심 아이디어**: adaptive spectral decomposition + SHAP-guided feature selection + probabilistic head.
- **강점**: 해석가능성(SHAP) + 불확실성 구간 동시 제공; 중국 남·북 지역 SOTA baseline 상회.
- **약점**: SHAP 계산 비용, spectral block hyper-param 민감.

### Relief (2025)
- **핵심 아이디어(추정)**: region-level ILI 예측 + 해석가능 rationale. 원 논문 직접 확인 실패 → **[unverified]**. RESEAT/SAIFlu-Net의 region-aware attention + LLM 기반 rationale 결합으로 추정.

---

## 4. 현재 SOTA & 미해결 문제

**벤치별 일반 경향** (저자 보고 기반, 재측정 검증 없음):
- US-Regions / US-States (CDC ILINet, weekly): Cola-GNN < EpiGNN < RESEAT ≈ MPSTAN
- Japan-Prefectures (IDWR, 47): CNNRNN-Res ≪ Cola-GNN < SAIFlu-Net < RESEAT
- Nowcasting (h=0, state-level): ARGONet, FaXNet 계열
- COVID / generalized epidemic: DeepGLEAM, MPSTAN, EINN

**미해결 문제**
1. **Regime shift robustness**: 팬데믹/NPI/백신 변화 시 과거 패턴 붕괴 — CALI-Net 이후 체계적 해법 부재.
2. **External signal 통합**: search/mobility/weather/텍스트 리포트를 통합하는 범용 framework 부재 → 본 repo가 LLM+CDC/IDWR 요약으로 접근.
3. **Explainability–accuracy trade-off**: FaXNet, Relief가 부분 해답이나 장기 horizon에서 품질 저하.
4. **Cross-domain transfer**: US ↔ Japan ↔ Korea pretrained ILI foundation model 부재 (TimeMoE/Chronos 등 일반 FM이 대체 중).
5. **Peak timing / onset 예측**: EpiDeep 이후 multi-task(peak + incidence) SOTA 공고화 모델 부족.

---

## 5. 참고 문헌

1. Wu et al. *Deep Learning for Epidemiological Predictions*. SIGIR 2018. https://doi.org/10.1145/3209978.3210077
2. Adhikari et al. *EpiDeep*. KDD 2019. https://doi.org/10.1145/3292500.3330917
3. Deng et al. *Cola-GNN*. CIKM 2020. https://doi.org/10.1145/3340531.3411975
4. Xie et al. *EpiGNN*. ECML-PKDD 2022. https://arxiv.org/abs/2208.11517
5. *RESEAT*. IEEE Access 2023. https://ieeexplore.ieee.org/document/10050036/
6. *MPSTAN*. Entropy 2024. https://arxiv.org/abs/2306.12436
7. Wu et al. *DeepGLEAM*. arXiv:2102.06684, 2021.
8. Yang, Santillana, Kou. *ARGO*. PNAS 2015. https://doi.org/10.1073/pnas.1515373112
9. Lu et al. *ARGONet*. Nature Communications 2019. https://doi.org/10.1038/s41467-018-08082-0
10. Zhu et al. *Attention-based RNN for influenza*. BMC Bioinformatics 2019. https://doi.org/10.1186/s12859-019-3131-8
11. *EINN*. arXiv:2411.17372, 2024.
12. *FaXNet*. Frontiers in Public Health 2026. https://doi.org/10.3389/fpubh.2026.1746529
13. Kamarthi et al. *CALI-Net*. AAAI 2021.
14. Awesome Epidemic Modeling Papers (KDD 2024). https://github.com/Emory-Melody/awesome-epidemic-modeling-papers

---

### 검증 상태 요약

| Model        | 원 논문 직접 확인     | 주요 숫자 확인        |
|--------------|:---------------------:|:---------------------:|
| CNNRNN-Res   | partial (abstract)    | unverified            |
| EpiDeep      | yes                   | partial (40% 주장)    |
| Cola-GNN     | yes (abstract/index)  | unverified exact      |
| EpiGNN       | yes (abstract)        | unverified            |
| SAIFlu-Net   | secondary only        | unverified            |
| RESEAT       | yes (abstract)        | unverified            |
| MPSTAN       | yes (abstract/HTML)   | unverified            |
| DeepGLEAM    | yes (abstract)        | partial               |
| ARGO/ARGONet | yes                   | yes (qualitative)     |
| EINN         | secondary             | unverified            |
| FaXNet       | secondary             | unverified            |
| Relief       | not found             | unverified            |

> 주의: IEEE Xplore(418) 및 arXiv PDF 바이너리 파싱 실패로 RESEAT/SAIFlu-Net/Cola-GNN의 Table 수치는 **unverified**. 본 repo의 TSF_models / neuralforecast 벤치에서 직접 재측정하여 이후 업데이트 권장.
