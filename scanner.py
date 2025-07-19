import pandas as pd
import ta
from utils import fetch_klines
import logging

def analyze_single_timeframe(df: pd.DataFrame) -> bool:
    # حساب مؤشرات EMA, RSI, MACD, ADX, Bollinger Bands
    df['EMA20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)

    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['ADX'] = adx

    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['bb_upper'] = bb.bollinger_hband()
    df['bb_middle'] = bb.bollinger_mavg()
    df['bb_lower'] = bb.bollinger_lband()

    latest = df.iloc[-1]

    # شروط الإشارة الفنية:
    ema_bullish = latest['EMA20'] > latest['EMA50']  # الاتجاه صعودي حسب EMA
    rsi_ok = 50 < latest['RSI'] < 70                # RSI في المنطقة المتوسطة إلى الصعودية
    macd_bullish = latest['MACD'] > latest['MACD_signal']  # تقاطع MACD إيجابي
    adx_strong = latest['ADX'] > 20                   # قوة الاتجاه جيدة
    bb_condition = latest['close'] < latest['bb_upper']   # السعر لم يصل بعد للتشبع الشرائي

    return all([ema_bullish, rsi_ok, macd_bullish, adx_strong, bb_condition])

def analyze_coin(symbol: str) -> bool:
    try:
        # تحليل متعدد الأطر الزمنية
        df_short = fetch_klines(symbol, interval='30m', limit=100)
        df_long = fetch_klines(symbol, interval='4h', limit=100)

        if df_short.empty or df_long.empty:
            logging.warning(f"⚠️ لا توجد بيانات كافية لـ {symbol}")
            return False

        short_signal = analyze_single_timeframe(df_short)
        long_trend = analyze_single_timeframe(df_long)

        # إشارة شراء فقط إذا تحقق الشرطان معاً
        return short_signal and long_trend

    except Exception as e:
        logging.error(f"❌ خطأ في تحليل {symbol}: {e}")
        return False
