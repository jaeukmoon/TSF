"""Reference adapter — Seasonal Naive baseline.
모델 등록 템플릿. 새 모델은 이 구조를 복사해서 forecast()만 교체하면 됨.
"""
import numpy as np

FREQ_SEASON = {"h": 24, "D": 7, "W": 52, "M": 12, "Q": 4, "Y": 1, "min": 60 * 24}


def forecast(context: np.ndarray, horizon: int, freq: str = "h") -> np.ndarray:
    context = np.asarray(context)
    single = context.ndim == 1
    if single:
        context = context[None, :]
    s = FREQ_SEASON.get(freq, 1)
    reps = int(np.ceil(horizon / s))
    tail = context[:, -s:] if context.shape[1] >= s else context[:, -1:]
    out = np.tile(tail, (1, reps))[:, :horizon]
    return out[0] if single else out
