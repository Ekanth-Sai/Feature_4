import pandas as pd
import numpy as np

def sma(series: pd.Series, window: int):
    return series.rolling(window).mean()

def ema(series: pd.Series, window: int):
    return series.ewm(span = window, adjust = False).mean()

def rsi(series: pd.Series, window: int = 14):
    delta = series.diff()
    up = delta.clip(lower = 0)
    down = -1 * delta.clip(upper = 0)
    ma_up = up.rolling(window = window, min_periods = 1).mean()
    ma_down = down.rolling(window = window, min_periods = 1).mean()
    rs = ma_up / (ma_down + 1e-9)
    return 100 - (100 / (1 + rs))