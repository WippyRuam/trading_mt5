# data_handler.py
import pandas as pd
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from config import BARS_PER_TF, ATR_PERIOD

# mapping to MT5 timeframe constants (keeps config simple)
TIMEFRAME_MAP = {
    '1D': mt5.TIMEFRAME_D1,
    '4H': mt5.TIMEFRAME_H4,
    '1H': mt5.TIMEFRAME_H1,
    '10M': mt5.TIMEFRAME_M10
}

def get_ohlc(symbol, timeframe_str, bars=BARS_PER_TF):
    tf = TIMEFRAME_MAP[timeframe_str]
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None or len(rates) < bars:
        print(f"[warn] Only {len(rates) if rates is not None else 0} bars for {symbol} {timeframe_str}")
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df[['time','open','high','low','close','tick_volume']]


def atr(df, period=ATR_PERIOD):
    high = df['high']
    low = df['low']
    close = df['close']
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_series = tr.rolling(window=period, min_periods=1).mean()
    return atr_series
