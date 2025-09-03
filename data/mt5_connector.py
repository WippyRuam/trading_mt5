import MetaTrader5 as mt5
from dotenv import load_dotenv 
import os 
from datetime import datetime
import time
load_dotenv()

# # establish connection to the MetaTrader 5 terminal
# if not mt5.initialize():
#     print("initialize() failed, error code =",mt5.last_error())
#     quit()

# print(mt5.version())

# account = os.getenv("username")
# password = os.getenv("password")
# server = os.getenv("server")

# authorized = mt5.login(account, password, server)
# if authorized:
#     print(f"Logged in successfully to account {account} on server {server}")
# else:
#     print(f"Failed to login, error code = {mt5.last_error()}")

# rate = mt5.copy_rates_from_pos('TSLA.NAS', mt5.TIMEFRAME_M1, 0, 10)
# print(rate)
# mt5.shutdown()
 

def connect_mt5():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize() failed, error code: {mt5.last_error()}")
    info = mt5.account_info()
    if info is None:
        raise RuntimeError("Failed to get account info; ensure MT5 terminal is running and logged in.")
    print(f"[mt5] Connected. Account: {info.login}")
    return info

def shutdown_mt5():
    mt5.shutdown()
    print("[mt5] Shutdown")

def ensure_symbol(symbol):
    si = mt5.symbol_info(symbol)
    if si is None:
        raise RuntimeError(f"Symbol {symbol} not found in MarketWatch")
    if not si.visible:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Failed to select symbol {symbol}")
    return si

def get_account_info():
    return mt5.account_info()

def get_tick(symbol):
    return mt5.symbol_info_tick(symbol)

def send_market_order(symbol, direction, volume, sl_price=None, tp_price=None, deviation=20, magic=123456):
    """
    direction: +1 buy, -1 sell
    """
    ensure_symbol(symbol)
    tick = get_tick(symbol)
    if tick is None:
        raise RuntimeError("No tick info for symbol")
    price = tick.ask if direction == 1 else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(volume),
        "type": mt5.ORDER_TYPE_BUY if direction == 1 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": float(sl_price) if sl_price is not None else 0.0,
        "tp": float(tp_price) if tp_price is not None else 0.0,
        "deviation": deviation,
        "magic": int(magic),
        "comment": "ARIMA_ETS_Strategy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    res = mt5.order_send(request)
    if res is None:
        raise RuntimeError("order_send returned None")
    if res.retcode != mt5.TRADE_RETCODE_DONE:
        print("[mt5] Order failed:", res)
        return None
    print("[mt5] Order placed. Ticket:", res.order)
    return res

def get_positions_by_magic(symbol=None, magic=None):
    pos = mt5.positions_get(symbol=symbol)
    if pos is None:
        return []
    if magic is None:
        return list(pos)
    return [p for p in pos if getattr(p, "magic", None) == magic]

def get_all_positions(symbol=None):
    pos = mt5.positions_get(symbol=symbol)
    return list(pos) if pos is not None else []

def modify_position_sl(position_ticket, symbol, new_sl):
    """
    Modify stop loss for a position.
    Uses TRADE_ACTION_SLTP request (works with modern MT5 builds).
    """
    req = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": int(position_ticket),
        "symbol": symbol,
        "sl": float(new_sl),
        # keep existing TP (0 if none)
    }
    res = mt5.order_send(req)
    if res is None:
        print("[mt5] modify_position_sl returned None")
        return False
    if res.retcode != mt5.TRADE_RETCODE_DONE:
        print("[mt5] modify SL failed:", res)
        return False
    print(f"[mt5] Modified SL of ticket {position_ticket} to {new_sl:.5f}")
    return True
