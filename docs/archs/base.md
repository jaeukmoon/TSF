# base — Seasonal Naive

Reference baseline used to validate the harness. Not a learned model.

## Algorithm

Given a context series of length `L` and a season length `s` (inferred from
`freq`), the forecast is the last period of the context, tiled to cover
`horizon` steps:

```
y_pred[t] = x_context[-s + (t mod s)]      for t = 0 ... horizon-1
```

Season length by `freq`:
- `h` (hourly) → 24
- `D` (daily)  → 7
- `W` (weekly) → 52
- `min`        → 60 × 24

## ASCII data flow

```
context (n_series × L)
        │
        ├── tail = context[:, -s:]          (last full season)
        │
        └── np.tile(tail, horizon / s)      (repeat + truncate)
                │
                ▼
         forecast (n_series × horizon)
```

## Pros

- Works offline, no training, no GPU
- Hard to beat when the dominant signal is a clean diurnal / weekly cycle
- Useful sanity check: if your fancy model can't beat this on ETTh1 h=96, something is wrong

## Cons

- Ignores trend, covariates, cross-series correlation
- Fails on non-stationary series (Exchange, Traffic during events)

## Source

`models/base/predict.py`:

```python
def forecast(context: np.ndarray, horizon: int, freq: str = "h") -> np.ndarray:
    s = FREQ_SEASON.get(freq, 1)
    reps = int(np.ceil(horizon / s))
    tail = context[:, -s:] if context.shape[1] >= s else context[:, -1:]
    return np.tile(tail, (1, reps))[:, :horizon]
```
