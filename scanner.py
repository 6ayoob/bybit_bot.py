import pandas as pd
import ta
from utils import fetch_klines

def analyze_coin(symbol: str, interval='30m', limit=100) -> bool:
    """
    يحلل العملة باستخدام EMA + RSI + MACD + ADX
    ويرجع True إذا توفرت إشارة شراء قوية.
    """
    df = fetch_klines(symbol, interval, limit)

    if df is None or df.empty or len(df) < 50:
        return False

    # حساب المؤشرات الفنية
    df['EMA20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)

    macd = ta.trend.macd(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()

    latest = df.iloc[-1]

    # شروط الدخول
    ema_trend = latest['EMA20'] > latest['EMA50']
    rsi_zone = 50 < latest['RSI'] < 70
    macd_cross = latest['MACD'] > latest['MACD_signal']
    adx_strong = latest['ADX'] > 20

    signal = ema_trend and rsi_zone and macd_cross and adx_strong

    return signal
