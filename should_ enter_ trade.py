import pandas as pd
import requests
import ta

def get_klines(symbol, interval='1h', limit=100):
    """
    جلب بيانات الشموع (Klines) من Bybit Spot API
    """
    url = "https://api.bybit.com/spot/quote/v1/kline"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('ret_code') != 0:
            print(f"API error: {data.get('ret_msg')}")
            return None

        klines = data.get('result', [])
        df = pd.DataFrame(klines)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']].copy()
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df

    except Exception as e:
        print(f"Error fetching klines: {e}")
        return None


def should_enter_trade(symbol):
    df = get_klines(symbol)
    if df is None or df.empty:
        return None  # لا يمكن اتخاذ قرار

    # حساب EMA9 و EMA21
    df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)

    # حساب RSI14
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)

    latest = df.iloc[-1]

    if pd.isna(latest['ema9']) or pd.isna(latest['ema21']) or pd.isna(latest['rsi']):
        return None

    # شروط شراء
    if latest['ema9'] > latest['ema21'] and latest['rsi'] < 30:
        return "Buy"

    # شروط بيع
    if latest['ema9'] < latest['ema21'] and latest['rsi'] > 70:
        return "Sell"

    return None  # لا إشارة واضحة


# اختبار سريع
if __name__ == "__main__":
    signal = should_enter_trade("BTCUSDT")
    print(f"Trade signal for BTCUSDT: {signal}")
