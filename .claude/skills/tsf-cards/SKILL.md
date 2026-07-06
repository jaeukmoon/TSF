---
name: tsf-cards
description: TSF 리더보드 트래커의 pending 요약카드를 이 Claude Code 세션이 직접 채우고 푸시한다 (wm-survey 2-tier 패턴 — CI는 수집/감지만, 요약은 구독 토큰). "TSF 카드 채워줘", "pending 카드 요약해줘" 류 요청에 사용.
---

# tsf-cards — pending 요약카드 채우기

CI(daily.yml)는 리더보드 수집·신규 감지·익명 모델 템플릿 카드까지만 한다(0 API 토큰).
공개 근거가 있는 신규 모델의 카드는 이 스킬로 로컬 Claude가 채운다.

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

## LTSF 탭 (data/ltsf.json) 갱신

새 LTSF 논문(ETT/Weather/ECL/Traffic/Exchange/ILI 성적 보고) 추가 요청 시:
- 논문 HTML(arxiv.org/html/<id>)에서 표를 **직접 읽어 전사**한다(기억으로 채우지 않는다. 못 읽으면 null).
- `data/ltsf.json`의 models 배열에 `{name, lookback, source{paper,arxiv,table}, results{dataset:{horizon:{mse,mae}}}}` 형식으로 추가.
- ILI horizon은 24/36/48/60 슬롯 사용(다른 데이터셋은 96/192/336/720).
