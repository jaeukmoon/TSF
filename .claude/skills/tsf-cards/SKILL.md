---
name: tsf-cards
description: TSF 리더보드 트래커의 pending 요약카드 + LTSF 신규 논문 큐(ltsf_pending)를 이 Claude Code 세션이 직접 처리하고 푸시한다 (wm-survey 2-tier 패턴 — CI는 수집/감지만, 요약·전사는 구독 토큰). "TSF 카드 채워줘", "LTSF 논문 반영해줘" 류 요청에 사용.
---

# tsf-cards — pending 요약카드 + LTSF 논문 큐 처리

CI(weekly.yml, 월 08:30 KST)는 리더보드 수집·신규 감지·익명 모델 템플릿 카드·LTSF 신규 논문
감지(watch_ltsf.py → data/ltsf_pending.json)까지만 한다(0 API 토큰).
공개 근거가 있는 신규 모델 카드와 LTSF 표 전사는 이 스킬로 로컬 Claude가 처리한다.

## 절차

1. `cd ~/github/TSF && git pull` (CI 봇 커밋 수신)
2. pending 확인:
   ```bash
   python3 -c "
   import json; c=json.load(open('data/cards.json'))
   p=[(k,v['name']) for k,v in c.items() if v['status']!='ok']
   print(len(p), p)"
   ```
   0개면 "pending 없음" 보고 후 종료.
3. 각 pending 모델에 대해 근거 수집 후 카드 생성:
   - 근거: `data/leaderboard.json`의 해당 엔트리(model_link/code_link/성적) + HF README(`https://huggingface.co/<repo>/raw/main/README.md`) + arXiv 검색(제목 일치 검증 필수).
   - 스키마는 `tracker/summarize.py`의 `CARD_SCHEMA`와 동일 (one_liner/summary/arch_type/org/strengths/weaknesses/paper_title/paper_url/is_documented).
   - 한국어, 기술용어 영어. 수치·링크 창작 금지. leakage Yes면 weaknesses에 명시.
   - pending이 5개 이상이면 general-purpose 서브에이전트로 배치 분할 생성.
4. `data/cards.json`에 병합: `card` 채우고 `status="ok"`, `generated_at=오늘`, `generated_by="claude-code"`.
5. 검증: `python3 -m json.tool data/cards.json > /dev/null` + 필수 필드 존재 확인.
6. 커밋/푸시 (`data: fill N summary cards`) → Pages는 push 트리거로 자동 배포.

## LTSF 탭 (data/ltsf.json) 갱신 — ltsf_pending 큐 처리

CI가 매주 arXiv에서 후보를 `data/ltsf_pending.json`에 쌓는다. 처리 절차:

1. 각 후보를 **triage**: 새 예측 모델 제안 + ETT류 벤치마크 full 표 보고 논문만 채택.
   서베이/벤치마크/포지션 논문, FM zero-shot 논문, 표 없는 논문은 기각.
2. 채택 논문: HTML(arxiv.org/html/<id>, 폴백 ar5iv)에서 **제안 모델 행만 직접 읽어 전사**
   (기억으로 채우지 않는다. 못 읽으면 null). 5편 이상이면 서브에이전트로 분할.
3. `data/ltsf.json` models 배열에 `{name, venue, lookback, source{paper,arxiv,table,short}, results{dataset:{horizon:{mse,mae}}}}` 추가.
   `venue`는 원 논문의 게재 학회("ICML 2025" 등) — arXiv abs 페이지 Comments/OpenReview로 **검증 후** 기입, 미게재·미확인이면 "arXiv".
   ILI horizon은 24/36/48/60 슬롯(다른 데이터셋은 96/192/336/720). 데이터셋 키: ETTh1/ETTh2/ETTm1/ETTm2/Weather/ECL/Traffic/Exchange/ILI.
4. 처리(채택/기각 불문)한 후보는 `ltsf_pending.json`에서 제거 (감지 이력은 `ltsf_seen.json`이 이미 보유 — 재감지 안 됨).
5. 커밋 메시지에 채택/기각 내역 한 줄씩.
