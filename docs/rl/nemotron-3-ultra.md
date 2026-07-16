---
title: Nemotron 3 Ultra
parent: RL Post-Training
---

# Nemotron 3 Ultra — Agentic RL Post-Training

**Paper**: [NVIDIA Nemotron 3 Ultra — 2606.15007](https://arxiv.org/abs/2606.15007) · NVIDIA · 2026-06
**Model**: 550B total / 55B active MoE, hybrid Mamba-2 + Attention, 1M context

**한 줄**: 20T 토큰을 NVFP4(4비트)로 프리트레이닝한 뒤 **SFT → 통합 RLVR → MOPD(멀티티처
온폴리시 증류) → MTP 부스팅**으로 에이전트·추론 능력을 끌어올린 오픈 모델. 경쟁 모델급
정확도에 디코드 스루풋은 최대 5~6배. XIF-RL 관점의 알맹이는 **§3 포스트트레이닝**이다.

> 이 문서는 **"직관 먼저, 기술 상세는 그 아래"** 구조다. 굵은 직관 문장만 따라가도 흐름이
> 잡히고, 표·수식은 근거용이다.

## 한눈에

| 항목 | 값 |
|---|---|
| 아키텍처 | 하이브리드 Mamba-2 + 드문 Attention, LatentMoE (108층, 층당 512 experts 중 top-22) |
| 규모 | 550B total / 55B active, MTP 헤드 2 (speculative decoding) |
| 프리트레이닝 | 20T 토큰, **NVFP4(4비트)**, 2단계(다양성 15T → 품질 5T), 1M 컨텍스트 확장 |
| 포스트트레이닝 | **SFT → RLVR(통합) → MOPD ×2 → MTP Boosting** |
| RL 알고리즘 | 비동기 GRPO (batch 8192, prompt당 16 rollout, gen 48K→64K) |
| 효율 | 디코드 스루풋 GLM-5.1 대비 5.9×, Qwen-3.5 대비 1.6× |

## 1. 아키텍처 — 왜 빠른가

**직관**: 보통 LLM은 Attention으로 앞 문장을 전부 기억해 길어질수록 느려진다. Nemotron은
**Mamba(요약본으로 압축해 들고 다니는 가벼운 기억)** 를 주로 쓰고 Attention은 꼭 필요한 곳에만
드문드문 둔다 → 긴 문맥에서 비용이 완만하고 KV 캐시가 작다. 여기에 **MoE**(전문가 512명 중
22명만 켬)로 "덩치는 크되 매번 쓰는 계산은 작게".

**기술**: 108층, model dim 8192, 층당 routed experts 512 / top-22, LatentMoE(latent 2048),
공유가중치 MTP 헤드 2개(네이티브 speculative decoding). Attention은 Q64/KV2(GQA).

## 2. 학습 파이프라인 개요

```
Base (NVFP4 20T + 1M ctx)
  → SFT (모범답안, 2단계 295K→515K 토큰)
  → RLVR (전 도메인 통합 자동채점 RL)
  → MOPD Warmup → MOPD ×2 (분야별 teacher 증류, 선생-학생 공진화)
  → MTP Boosting (드래프트 헤드만 미세조정 → 생성 가속)
```

## 3. RLVR — "자동 채점"이 실제로 어떻게 되나 (우리와 같은 계열)

**직관**: RLVR의 "Verifiable"은 **사람 없이 객관적으로 자동 채점되는 문제만 골라 쓴다**는 뜻이다.
도메인마다 채점기(verifier)가 다르다:

| 도메인 | 자동 채점 방식 | 보상 |
|---|---|---|
| 수학 | 정답과 비교(LLM 판정기 확인) | 맞음/틀림 |
| 코드/경쟁PS | 생성 코드를 **숨은 테스트에 실행** | 통과율 |
| SWE | 패치 적용 후 **숨은 테스트 실행** | 이진 |
| 터미널/에이전트 | 환경이 작업 완료 판정 | 성공/실패 |
| 지시 따르기 | 규칙을 **프로그램으로 검사** | 충족 여부 |
| 안전(인젝션 방어) | **결정적 verifier**: 위험 도구 호출 여부 | 이진 |
| 챗(주관적) | 예외 — **채점 모델(GenRM)** 이 두 답 비교 | 학습된 판정 |

**채점 → 학습**: 한 문제에 답 16개 생성 → 각각 채점 → 같은 문제 16개 평균을 빼는
**group-relative advantage**(GRPO, critic 없음) → 평균보다 잘한 답의 토큰 확률↑. 학습 전
**reward profiling**, Gaussian 기반 데이터 믹스, 비동기 GRPO(batch 8192, gen 48K→64K).

> **XIF-RL 시사점**: 통제 비교를 위해 학습 전 보상 분포를 프로파일링하는 절차는 CRPO sweep
> 전 v2 parquet 점검에 그대로 차용 가능.

## 4. MOPD — 여러 선생님을 하나로 (이 논문의 핵심)

**왜**: RLVR에 도메인을 늘릴수록 한 배치에 각 도메인 샘플이 조금씩만 들어가 **신호가 희석**된다.
→ 분야별 **전문 teacher를 10+개** 따로 키운 뒤 학생에 합친다.

**RLVR과 결정적 차이 = 보상이 촘촘하다(dense)**:
- RLVR: 답을 다 만든 뒤 "정답 맞았냐"로 **끝에 한 번**(sparse).
- MOPD: 학생이 답을 만들면 teacher가 **토큰 하나하나** 채점(dense).

토큰마다 **"teacher의 이 단어 확신도 − 학생의 확신도"** 를 학습 신호(sampled reverse-KL)로 쓴다:

$$\hat{A}_t = \log \pi_{\text{teacher}}(y_t \mid s_t) - \log \pi_{\text{student}}(y_t \mid s_t)$$

핵심은 **학생이 스스로 만든 답 위에서 채점(on-policy)** 한다는 점(모범답안 베끼기가 아님).
비동기 파이프라인(생성/채점/학습 겹침)에서 behavior/proximal 정책 분리 + PPO 클리핑 + IcePop
마스킹으로 안정화. gen 192K, batch 1024, prompt당 rollout 1개.

**Warmup 필수**: teacher-student가 다른 SFT로 자라면 학생 답이 teacher에게 낯설어(OOD) 채점
불가 → teacher 분포로 학생을 가볍게 SFT해 겹쳐준다. 에이전트 도메인에서 큰 효과, 순수 추론
(HLE)엔 무효.

**2회차 = 선생님 다시 키우기 (공진화)**: teacher는 *Ultra 복제본에 한 분야만 추가 특훈(분야
SFT+RL, 때론 더 센 외부 모델 데이터)* 시킨 것. 1회차 증류로 학생이 teacher의 70~90%를
따라잡으면 → **강해진 학생(MOPD1)을 새 출발점으로 teacher를 재특훈** → 더 높은 천장의 새
teacher 생성 → 다시 증류. 여전히 앞서는 1회차 teacher는 재사용. (덤: 새 teacher가 학생
출신이라 분포가 비슷해 증류가 더 잘 붙음.)

**언제 되고 안 되나**:
- ✅ teacher 우위가 "학생이 **이미 낼 수 있는** 답들 중 취향"일 때(도구 호출·기권 등) → 회수율 70~170%, 일부는 teacher 초월.
- ❌ 우위가 "학생이 **안 해본 새 풀이**"에서 올 때(HLE 16.9%) — 학생이 시도조차 안 하니 채점할 문장이 안 나옴. on-policy 증류의 근본 한계.

> **XIF-RL 시사점**: (1) 다성분 보상 희석 문제를 그들은 teacher 분리+증류로 풀었다 — 우리 규모
> 에선 성분별 가중 스케줄이 현실적 대응. (2) 미완료 rollout loss 마스킹 + malformed 토큰 음의
> advantage는 우리 format 보상을 토큰 레벨로 옮기는 옵션. (3) abstention reward 동적 캘리브레이션
> ↔ CRPO calibration 항 가중 스케줄링.

## 5. 그 외 (압축)

- **Reasoning budget control**: off/medium/regular 3모드. medium은 토큰 2.5× 절감 / 정확도 ~7%
  하락. RLVR 프롬프트의 2.5%에만 length 기반 reward를 넣어도 전 도메인으로 일반화.
- **양자화(§4)**: 학습 후 NVFP4로 PTQ, 부위별 혼합 정밀도(routed=NVFP4, 공유·Mamba=FP8,
  attention·embedding·MTP=BF16). 5.03 BPE 선택 시 BF16과 거의 동일 정확도. 체크포인트 하나로
  Blackwell(W4A4)·Hopper(W4A16) 커버.
- **추론(§5)**: 프리필(연산 병목)은 활성 55B라 불리, **디코드(메모리 병목)는 Mamba의 길이-무관
  일정 비용 덕에 우위**. MTP speculative decoding으로 단일 사용자 2.89×. RL 학습에서도 rollout
  생성 가속(1.46×)에 같은 MTP를 씀.

## Weaknesses / 한계

- **MOPD는 학생 사정권 밖 능력은 못 가르친다** (HLE 회수율 16.9%). 새로운 추론 경로가 필요한
  능력은 off-policy 데이터가 별도로 필요.
- 에이전트·행동 패턴(도구 사용, 다단계 실행)에 강한 방법이지 순수 추론 부양책은 아님.
- 파이프라인이 무겁다(teacher 10+개, 2회차 공진화, 비동기 인프라) — 소규모 재현 난이도 높음.

## XIF-RL 적용 요약

1. **SFT→통합 RLVR + 사전 reward profiling** — 우리 파이프라인과 동형, sweep 전 보상 점검 차용.
2. **보상 희석 대응** — teacher 증류 대신 CRPO 성분별 가중 스케줄.
3. **약한 judge는 뚫린다** — timemaster의 hard 게이트 유지 정당화(그들은 Ultra급 GenRM 사용).
4. **abstention 동적 캘리브레이션** ↔ CRPO calibration 가중 스케줄.
5. **held-out gate 평가** — 특정 시즌·지역을 개발 중 안 보는 게이트로 예약해 일반화 정직 검증.
