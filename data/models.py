# models.py
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

FORECAST_H = 5  # default, but main will supply config.FORECAST_H if needed

def fit_arima_forecast(series, h=FORECAST_H):
    try:
        model = ARIMA(series, order=(1,1,1))
        res = model.fit()
        f = res.forecast(steps=h)
        return np.array(f)
    except Exception as e:
        print("[models] ARIMA fit error:", e)
        return np.repeat(series.iloc[-1], h)

def fit_ets_forecast(series, h=FORECAST_H):
    try:
        model = ExponentialSmoothing(series.astype(float), trend='add', seasonal=None, initialization_method='estimated')
        res = model.fit()
        f = res.forecast(h)
        return np.array(f)
    except Exception as e:
        print("[models] ETS fit error:", e)
        return np.repeat(series.iloc[-1], h)

def combined_forecast(series, h=FORECAST_H):
    ar = fit_arima_forecast(series, h=h)
    et = fit_ets_forecast(series, h=h)
    combo = (ar + et) / 2.0
    return combo

def forecast_direction(last_price, forecast, deadzone_pct=0.00005):
    mean_f = float(forecast.mean())
    pct_change = (mean_f - last_price) / last_price
    if pct_change > deadzone_pct:
        return 1
    elif pct_change < -deadzone_pct:
        return -1
    else:
        return 0
