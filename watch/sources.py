"""XIF-RL RL-Watch 설정 (zero-dep, importable).

fetch_papers.py 가 import 한다. WM/surveybot/sources.py 의 구조를 이식(provenance:
같은 dict-모듈 패턴, third-party dep 0). 도메인만 WAM/VLA → RL×시계열/RL알고리즘으로 교체.
공통 개선은 WM 쪽 sources.py 에도 반영할 것 (두 사이트 같이 수정 원칙).
"""

# arXiv 카테고리 (recency pull → 로컬 키워드 필터). RL-for-TSF 는 cs.LG/stat.ML,
# LLM RL(GRPO 계열)은 cs.LG/cs.CL/cs.AI 에 주로 올라온다.
ARXIV_CATEGORIES = ["cs.LG", "stat.ML", "cs.AI", "cs.CL"]

# --- Gate A: RL × 시계열 교집합 (둘 다 매치해야 통과; 교집합이 희귀해 추가 게이트 없음) ---
TS_PHRASES = ["time series", "time-series", "forecast", "temporal prediction"]
RL_PHRASES = [
    "reinforcement learning", "policy optimization", "policy optimisation",
    "policy gradient", "reward function", "reward model", "reward design",
    "verifiable reward",
]
# 단어경계 + 대소문자 구분 (fetch 쪽에서 \b 붙임) — "grpo" 소문자 일반단어 오탐 없음
RL_ACRONYMS = ["RL", "GRPO", "PPO", "RLVR", "RLHF", "DPO", "RLAIF"]

# --- Gate B: RL 알고리즘 트렌드 (LLM/reasoning 문맥 + 신호 게이트) ---
# 제목에 RL 핵심구가 있어야 함 (abstract 만 매치 = 응용논문이 대부분이라 노이즈)
ALGO_TITLE_PHRASES = [
    "reinforcement learning", "policy optimization", "policy optimisation",
    "reward model", "reward hacking", "verifiable reward", "rlvr", "rlhf",
    "test-time reinforcement",
]
# 제목에 알고리즘 이름 자체가 있으면 게이트(탑학회/빅테크/HF) 무관 포함 — 정확히 추적 대상
ALGO_NAME_ACRONYMS = ["GRPO", "DAPO", "GSPO", "RLOO", "REINFORCE", "CISPO", "GMPO"]
# LLM 문맥 anchor (title+abstract lowercase substring)
LLM_ANCHORS = ["language model", "llm", "reasoning", "post-train", "post train", "chain-of-thought"]
# 게이트 통과용 HF upvote 하한 (HF daily 노출 자체도 신호)
HF_UPVOTE_MIN = 5

# --- Gate C: 강제 포함 (게이트 무관 무조건 카드) ---
# (1) baseline watch: tracked baseline 인용/비교 논문.
#     비교 언급은 보통 본문 실험 섹션에 있음 → fetch_papers.py 가 키워드 통과 후보에
#     한해 arXiv HTML 본문도 스캔 (WM 의 FastWAM/ImageWAM watch 와 동일 패턴).
#     값은 regex 조각 (단어경계는 호출부, IGNORECASE — "Time-R1"/"TimeR1" 흡수).
TRACKED_BASELINES = {
    "Time-R1": r"time[\s‐–-]?r1",
    "TimeMaster": r"time[\s‐–-]?master",
    "PostTime": r"post[\s‐–-]?time",
    "CastFlow": r"cast[\s‐–-]?flow",
    "KairosAgent": r"kairos[\s‐–-]?agent",
}
# (2) 역학/ILI 예측 — epidemic forecasting 추적 (lowercase substring)
EPI_PHRASES = [
    "influenza", "epidemic forecast", "epidemic prediction",
    "epidemiological forecast", "disease forecast", "outbreak forecast",
    "flu season",
]
EPI_ACRONYMS = ["ILI"]  # 단어경계 + 대소문자 구분

# --- Gate D: 예측(TSF) 트렌드 — RL 무관 최신 예측 논문 (2열 뷰의 '예측 축') ---
# 제목에 예측 핵심구가 있어야 함 (abstract-only 매치 = 응용/도메인 논문 노이즈)
# 일반 경로는 **탑학회 게재(수락 공지)만** 통과 (2026-07-12 사용자: 예측 축은 탑학회
# 게재 + 완성도 높은 논문 위주). 강제 포함 ①②(연구축·모델명)는 게이트 면제 유지.
TSF_TITLE_PHRASES = ["time series", "time-series", "forecast"]
# 무게이트 강제 포함 ①: 확률예측/보정 — probabilistic forecasting 추적 (title+abstract)
TSF_HOT_PHRASES = [
    "probabilistic forecast", "quantile forecast", "quantile regression",
    "conformal prediction", "calibrated forecast", "distributional forecast",
    "interval forecast", "proper scoring", "crps",
]
# 네거티브: 제목이 비예측 태스크인데 'forecast' 도 없으면 Gate D 탈락
# (실측 2026-07-12: CAAD anomaly detection 이 'time series'+KDD 신호로 통과)
TSF_NEG_TITLE = ["anomaly", "classification", "imputation", "clustering", "segmentation"]
# 무게이트 강제 포함 ②: 시계열 파운데이션/대표 모델명 (title lowercase substring)
TSF_MODEL_TOKENS = [
    "chronos", "timesfm", "moirai", "time-moe", "timemoe", "sundial", "tirex",
    "toto", "lag-llama", "timegpt", "patchtst", "itransformer", "dlinear",
    "timesnet", "time-llm", "timellm", "uni2ts", "timer-xl",
]

# --- 빅테크/프론티어 랩 탐지 (RL 계열 논문 주 생산처) ---
# affil: title+abstract+authors 합본 lowercase substring
# affil_strict=True: 저자 blob 에서만 매칭 (abstract 의 모델명 인용 오탐 방지 — WM 실측 이식)
BIGTECH_ORGS = {
    "Google DeepMind": {"affil": ["google deepmind", "deepmind", "google research"]},
    "OpenAI":          {"affil": ["openai"], "affil_strict": True},
    "Anthropic":       {"affil": ["anthropic"], "affil_strict": True},
    "Meta FAIR":       {"affil": ["meta ai", "fair", "facebook ai", " meta,", "meta platforms", "meta superintelligence"]},
    "DeepSeek":        {"affil": ["deepseek"], "affil_strict": True},
    "Alibaba/Qwen":    {"affil": ["alibaba", "qwen", "tongyi"], "affil_strict": True},
    "ByteDance Seed":  {"affil": ["bytedance", "seed team"]},
    "Moonshot/Kimi":   {"affil": ["moonshot", "kimi team"], "affil_strict": True},
    "Microsoft Research": {"affil": ["microsoft research", "microsoft "]},
    "NVIDIA":          {"affil": ["nvidia"]},
    "Mistral":         {"affil": ["mistral ai"], "affil_strict": True},
    "Amazon/AWS":      {"affil": ["amazon", "aws ai"], "affil_strict": True},
    "Salesforce":      {"affil": ["salesforce"], "affil_strict": True},  # 시계열 FM(Moirai) 생산처
    "Tencent":         {"affil": ["tencent", "hunyuan"], "affil_strict": True},
}

# 제목 모델명 토큰 (affil 누락돼도 프론티어 포착) — lowercase substring on title
BIGTECH_TITLE_TOKENS = [
    "deepseek", "qwen", "kimi", "gemini", "llama", "gpt-oss", "chronos", "moirai",
    "timesfm", "time-moe", "timemoe",
]

# 탑학회 venue 토큰 (arXiv comment lowercase 스캔) — ML/NLP/DM 중심 + 시계열 단골 KDD
TOP_CONF = [
    "neurips", "nips", "icml", "iclr", "aaai", "ijcai", "acl", "emnlp", "naacl",
    "colm", "aistats", "uai", "kdd", "www", "cikm",
]

# watch_type 분류 (build_site.py 섹션/배지가 참조)
WATCH_TYPES = {
    "baseline": "⚡ 비교군 인용 (Time-R1/TimeMaster)",
    "epi": "역학/ILI 예측",
    "rl_tsf": "RL × 시계열",
    "algo": "RL 알고리즘 트렌드",
    "tsf_trend": "예측 트렌드 (non-RL)",
}

# 2열 레이아웃 — watch 페이지의 축 배치 (build_site.py가 참조)
WATCH_AXES = [
    ("RL 축", ["baseline", "rl_tsf", "algo"]),
    ("예측 축", ["epi", "tsf_trend"]),
]
