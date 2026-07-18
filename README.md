# TSF Leaderboard Tracker

시계열 예측(TSF) 파운데이션 모델의 **주간 자동 리더보드 미러 + 연구 워치** 사이트.

🔗 **라이브**: https://jaeukmoon.github.io/TSF/

루트 `index.html`(단일 파일 앱) + `data/*.json` 을 GitHub Pages 가 그대로 서빙한다
(`.nojekyll`, Jekyll 미사용). 아래 "레거시 harness" 섹션의 `models/`·`run.py`·`docs/` 는
초기 벤치마크 하네스의 잔재이며 **라이브 사이트와 무관**하다.

## 탭 구성 (4탭 허브)

| 탭 | 내용 | 데이터 |
|---|---|---|
| 🏆 **리더보드** | GIFT-Eval + fev-bench 공식 집계 재현 + **LTSF 논문성적**(ETT·ILI 등 37모델, 논문 보고 수치) | `data/leaderboard.json`, `data/ltsf.json` |
| 📇 **모델 요약** | 신규 모델 요약 카드(one-liner·강약점·아키텍처/조직 배지·GIFT/fev 스탯) | `data/cards.json` |
| 📡 **RL Watch** | XIF-RL 연구 워치의 **정제 공개 미러**(논문 사실 요약만) | `data/rl_watch.json` |
| 🔒 **Lab** | 암호화된 연구 노트(AES-256-GCM, 브라우저 복호화) | `data/lab.enc.json` |

## 자동화 파이프라인

```
weekly.yml (월 08:30 KST cron)
  └─ tracker/update.py
       ├─ fetch_gift.py   GIFT-Eval HF space 재집계(config별 Seasonal-Naive 정규화 → MASE/CRPS geomean + rank)
       ├─ fetch_fev.py    fev-bench 재집계(baseline 상대오차 win_rate + skill_score)
       ├─ summarize.py    2-tier: CI는 익명모델 zero-LLM 템플릿 카드만; 근거 있는 신규는 pending
       └─ watch_ltsf.py   주간 arXiv 감지 → ltsf_pending.json 큐(0-LLM, seen 원장 dedup)
  └─ data/ 커밋 → deploy-pages(pages.yml) → Pages 갱신
```

- **모델 카드 채우기**: `/tsf-cards` (레포 `.claude/skills/`) — CI가 남긴 pending 카드와
  `ltsf_pending.json`의 신규 LTSF 논문을 **로컬 Claude 세션이 전사**(API 키 불필요, 2-tier).
- **RL Watch 미러**: XIF-RL(비공개)의 `research_site/export_public.py` 가 단방향으로
  `data/rl_watch.json`(정제) + `data/lab.enc.json`(암호화) 를 이 레포에 기록.

## 집계 방법 (요약)

- **GIFT-Eval**: config별(97개) Seasonal-Naive 정규화 후 MASE[0.5]·CRPS geometric mean + config별 rank 평균.
- **fev-bench**: baseline "Seasonal naive" 대비 상대오차 clip[1e-2,100], pairwise win_rate + skill_score(1−gmean).
- **LTSF 논문성적**: 각 논문이 보고한 test MSE/MAE 를 직접 전사(프로토콜은 Source 칼럼으로 구분).
  lookback·프로토콜이 소스마다 달라 행 간 직접 비교는 주의.

각 벤치마크의 공식 수치와 미세한 차이가 있을 수 있다(재현 집계).

## 데이터 파일

| 파일 | 내용 |
|---|---|
| `data/leaderboard.json` | GIFT-Eval + fev-bench 순위 + `first_seen` 원장 |
| `data/ltsf.json` | LTSF 37모델 × ETT/Weather/ECL/Traffic/Exchange/ILI (수기 전사) |
| `data/cards.json` | 모델 요약 카드 |
| `data/ltsf_pending.json` · `ltsf_seen.json` | 주간 arXiv 감지 큐 + dedup 원장 |
| `data/rl_watch.json` · `lab.enc.json` | XIF-RL 미러(정제/암호화) |

## 레거시 harness (라이브 아님)

`models/`, `benchmarks/`, `run.py`, `leaderboard.py`, `docs/`(모델 계보·SOTA 레퍼런스),
`leaderboard.html` 은 초기 "plug-and-play 평가 프레임워크" 잔재다. 라이브 트래커는 이를
쓰지 않으며, 문서 참고용으로만 남겨둔다. (`docs/sota_2026.md`, `docs/model_history.md`,
`docs/ili_lineage.md` 는 여전히 유효한 계보 노트.)

## License

MIT.
