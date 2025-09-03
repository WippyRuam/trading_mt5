# strategy.py
import numpy as np
from config import PROXIMITY_ATR_MULT

def timeframes_agree(directions):
    """
    directions: dict tf->-1/0/1
    require at least 3 non-neutral agreeing signals
    """
    vals = [v for v in directions.values() if v != 0]
    if len(vals) < 2:
        return 0
    s = sum(vals)
    if s == len(vals):
        return 1
    if s == -len(vals):
        return -1
    return 0

def nearby_check(latest_closes, atr_reference):
    # latest_closes: dict tf->price
    closes = np.array(list(latest_closes.values()), dtype=float)
    diff = np.max(closes) - np.min(closes)
    return diff <= atr_reference * PROXIMITY_ATR_MULT

def decide_trade(directions, latest_closes, atr_ref):
    agree = timeframes_agree(directions)
    prox = nearby_check(latest_closes, atr_ref)
    return agree, prox
