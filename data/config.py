# config.py
SYMBOL = "EURUSDm"
TIMEFRAMES = {
    '1D':  None,  # just placeholders for documentation
    '4H':  None,
    '1H':  None,
    '10M': None
}
# NOTE: TIMEFRAME ids are referenced in data_handler via mt5 constants to avoid circular import
BARS_PER_TF = 500
FORECAST_H = 5
RISK_PERCENT = 1.0
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.5
ATR_MULTIPLIER_TRAIL = 0.8
PROXIMITY_ATR_MULT = 1.5
MAX_LOT = 5.0
MIN_LOT = 0.01
SLEEP_BETWEEN_MONITOR = 5  # seconds between trailing-stop checks
MAGIC = 123456
