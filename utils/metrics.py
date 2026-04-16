import numpy as np


def mse(y_true, y_pred):
    return float(np.mean((y_true - y_pred) ** 2))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(y_true - y_pred)))


def mase(y_true, y_pred, y_train, seasonality=1):
    # Mean Absolute Scaled Error
    naive = np.mean(np.abs(y_train[seasonality:] - y_train[:-seasonality]))
    if naive == 0:
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)) / naive)


def crps_sample(y_true, samples):
    # samples: (..., n_samples, horizon)  — empirical CRPS
    samples = np.asarray(samples)
    y_true = np.asarray(y_true)
    n = samples.shape[-2]
    term1 = np.mean(np.abs(samples - y_true[..., None, :]), axis=-2)
    diff = np.abs(samples[..., :, None, :] - samples[..., None, :, :])
    term2 = 0.5 * diff.mean(axis=(-3, -2))
    return float(np.mean(term1 - term2))
