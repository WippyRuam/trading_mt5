# trailing_stop.py
import time
import mt5_connector as mt5c
from config import ATR_MULTIPLIER_TRAIL, SLEEP_BETWEEN_MONITOR, MAGIC

def trailing_monitor(symbol, position_ticket, direction, atr_ref):
    """
    direction: +1 buy, -1 sell
    position_ticket: ticket id of the opened position
    """
    print("[trail] Entering trailing monitor for ticket", position_ticket)
    while True:
        positions = mt5c.get_all_positions(symbol=symbol)
        # find our position
        pos = None
        for p in positions:
            if p.ticket == position_ticket and getattr(p, "magic", None) == MAGIC:
                pos = p
                break
        if pos is None:
            print("[trail] Position closed or not found. Exiting trailing monitor.")
            return

        tick = mt5c.get_tick(symbol)
        if tick is None:
            time.sleep(SLEEP_BETWEEN_MONITOR)
            continue

        current_price = tick.bid if pos.type == 0 else tick.ask  # pos.type: 0 buy, 1 sell
        trailing_dist = ATR_MULTIPLIER_TRAIL * atr_ref

        if direction == 1:
            new_sl = current_price - trailing_dist
            if pos.sl == 0.0 or new_sl > pos.sl and new_sl < current_price:
                success = mt5c.modify_position_sl(position_ticket, symbol, new_sl)
                if success:
                    pos.sl = new_sl
        else:
            new_sl = current_price + trailing_dist
            if pos.sl == 0.0 or new_sl < pos.sl and new_sl > current_price:
                success = mt5c.modify_position_sl(position_ticket, symbol, new_sl)
                if success:
                    pos.sl = new_sl

        time.sleep(SLEEP_BETWEEN_MONITOR)
