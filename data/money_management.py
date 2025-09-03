# money_management.py
import mt5_connector as mt5c
from config import RISK_PERCENT, MAX_LOT, MIN_LOT
import MetaTrader5 as mt5

def calc_lot_size(symbol, account_balance, risk_percent, stop_distance_price):
    """
    Very practical approximate lot sizing:
    - Estimate loss per 1.0 lot for stop_distance_price using symbol tick info.
    - Fallback to $10 per pip for majors when info missing.
    stop_distance_price is in price units (e.g. 0.0012)
    """
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print("[mm] No tick info, using min lot")
        return MIN_LOT
    sym = mt5.symbol_info(symbol)
    if sym is None:
        print("[mm] No symbol_info, using min lot")
        return MIN_LOT

    try:
        # Approximate pip value per lot:
        pip_value_per_lot = (sym.trade_contract_size * sym.tick_value) / sym.tick_size
    except Exception:
        pip_value_per_lot = 10.0

    point = sym.point
    pip_count = stop_distance_price / point if point > 0 else 1.0
    loss_per_lot = pip_value_per_lot * pip_count
    if loss_per_lot <= 0:
        return MIN_LOT
    risk_amount = account_balance * (risk_percent / 100.0)
    lots = risk_amount / loss_per_lot
    lots = max(min(lots, MAX_LOT), MIN_LOT)
    # round to volume_step
    vol_step = sym.volume_step
    min_lot = sym.volume_min
    max_lot = sym.volume_max
    try:
        # round to nearest step
        steps = round(lots / vol_step)
        lots = steps * vol_step
        lots = max(min_lot, min(max_lot, lots))
    except Exception:
        pass
    return float(lots)
