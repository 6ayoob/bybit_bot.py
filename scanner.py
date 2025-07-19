import pandas as pd
import ta
from utils import fetch_klines


def analyze_single_timeframe(df: pd.DataFrame) -> bool:
    # مؤشرات EMA + RSI + MACD + ADX + Bollinger Bands
    df['EMA20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)

    macd = ta.trend.macd(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx.adx()

    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_middle'] = bb.bollinger_mavg()
    df['bb_lower'] = bb.bollinger_lband()

    latest = df.iloc[-1]

    # شروط الإشارة الفنية
    ema_bullish = latest['EMA20'] > latest['EMA50']
    rsi_ok = 50 < latest['RSI'] < 70
    macd_bullish = latest['MACD'] > latest['MACD_signal']
    adx_strong = latest['ADX'] > 20
    bb_condition = latest['close'] < latest['bb_upper']  # لم يصل للتشبع

    return ema_bullish and rsi_ok and macd_bullish and adx_strong and bb_condition


def analyze_coin(symbol: str) -> bool:
    """
    تحليل متعدد الأطر الزمنية باستخدام:
    - 30 دقيقة للإشارة
    - 4 ساعات لتأكيد الاتجاه العام
    """
    df_short = fetch_klines(symbol, interval='30m', limit=100)
    df_long = fetch_klines(symbol, interval='4h', limit=100)

    if df_short.empty or df_long.empty:
        return False

    short_signal = analyze_single_timeframe(df_short)
    long_trend = analyze_single_timeframe(df_long)

    # فقط إذا كان الاتجاه العام مؤكد والإشارة قصيرة المدى موجودة
    return short_signal and long_trend
