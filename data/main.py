# main.py
import time
from config import SYMBOL, BARS_PER_TF, FORECAST_H, ATR_MULTIPLIER_SL, RISK_PERCENT, MAGIC
import mt5_connector as mt5c
import data_handler as dh
import models as md
import strategy as strat
import money_management as mm
import trailing_stop as ts
from data_handler import TIMEFRAME_MAP

def main():
    # Connect
    mt5c.connect_mt5()
    try:
        # 1) fetch data
        dfs = {}
        latest_closes = {}
        atr_values = {}
        for tf_name in TIMEFRAME_MAP.keys():
            print(f"[main] fetching {tf_name}")
            df = dh.get_ohlc(SYMBOL, tf_name, bars=BARS_PER_TF)
            dfs[tf_name] = df
            latest_closes[tf_name] = float(df['close'].iloc[-1])
            atr_series = dh.atr(df)
            atr_values[tf_name] = float(atr_series.iloc[-1])

        # pick ATR reference from smallest TF (10M)
        atr_ref = atr_values.get('10M', sum(atr_values.values())/len(atr_values))

        # 2) model + forecast + direction per TF
        directions = {}
        forecasts = {}
        for tf_name, df in dfs.items():
            series = df['close'].astype(float)
            combo = md.combined_forecast(series, h=FORECAST_H)
            forecasts[tf_name] = combo
            dirn = md.forecast_direction(series.iloc[-1], combo)
            directions[tf_name] = dirn
            print(f"[main] {tf_name}: last={series.iloc[-1]:.5f}, mean_forecast={combo.mean():.5f}, dir={dirn}")

        # 3) decision
        agree, prox = strat.decide_trade(directions, latest_closes, atr_ref)
        print(f"[main] agreement={agree}, proximity={prox}")
        if agree == 0 or not prox:
            print("[main] No trade. Exiting.")
            return

        # 4) prepare order
        last_price = latest_closes['10M']
        sl_distance = ATR_MULTIPLIER_SL * atr_ref
        if agree == 1:
            sl_price = last_price - sl_distance
        else:
            sl_price = last_price + sl_distance

        account = mt5c.get_account_info()
        balance = float(account.balance)
        lots = mm.calc_lot_size(SYMBOL, balance, RISK_PERCENT, sl_distance)
        print(f"[main] Placing {'BUY' if agree==1 else 'SELL'} lots={lots:.2f} sl={sl_price:.5f}")

        res = mt5c.send_market_order(SYMBOL, agree, lots, sl_price=sl_price, tp_price=None, magic=MAGIC)
        if res is None:
            print("[main] order failed")
            return

        # find the resulting position ticket: wait briefly for positions to be registered
        time.sleep(1.0)
        positions = mt5c.get_positions_by_magic(symbol=SYMBOL, magic=MAGIC)
        if len(positions) == 0:
            # fallback: get any recent position
            all_pos = mt5c.get_all_positions(symbol=SYMBOL)
            if len(all_pos) == 0:
                print("[main] no position found after order. Exiting.")
                return
            pos = all_pos[-1]
        else:
            pos = positions[-1]
        ticket = pos.ticket

        # 5) trailing monitor
        ts.trailing_monitor(SYMBOL, ticket, agree, atr_ref)

    finally:
        mt5c.shutdown_mt5()

if __name__ == "__main__":
    main()
