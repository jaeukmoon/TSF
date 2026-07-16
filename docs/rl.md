---
title: RL Post-Training
layout: default
nav_order: 7
has_children: true
---

# RL Post-Training for Forecasting & Reasoning

LLM 포스트트레이닝(특히 **RL**) 논문들의 딥다이브. 시계열 예측에 LLM을 RL로 학습시키는
관점(XIF-RL)에서 읽은 스터디 노트다. 각 문서는 **"직관 먼저, 기술 상세는 그 아래"** 구조 —
굵은 직관 문장만 따라가도 흐름이 잡히고, 표·수식은 근거용이다.

## 수록 딥다이브

| 문서 | 논문 | 핵심 | 상태 |
|---|---|---|---|
| [Nemotron 3 Ultra](rl/nemotron-3-ultra.html) | [2606.15007](https://arxiv.org/abs/2606.15007) | SFT→통합 RLVR→MOPD(멀티티처 온폴리시 증류)→MTP. 에이전트 중심 대규모 RL 파이프라인 | ✅ |

## 큐 (예정)

- **MOPD** ([2606.30406](https://arxiv.org/abs/2606.30406)) — Nemotron이 쓴 멀티티처 온폴리시 증류의 원조 논문
- **MAI-Thinking-1** (Microsoft) — from-scratch 추론 모델, STEM/agentic RL 스페셜리스트 통합
- **Time-R1 / TimeMaster** — 시계열 RL 비교군 (XIF-RL `research_site`에서 이관 검토)

> XIF-RL 레포는 연구 코드 전용으로 유지하고, 스터디/딥다이브 정리본은 이 사이트에 모은다.
