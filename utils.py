import pandas as pd
from pybit.unified_trading import HTTP
import time
import logging

# تهيئة عميل Bybit بدون مفاتيح (للقراءة فقط)
session = HTTP(testnet=False)

def fetch_klines(symbol: str, interval: str = '30m', limit: int = 100) -> pd.DataFrame:
    """
    جلب بيانات الشموع (Klines) من Bybit Spot
    """
    try:
        response = session.get_kline(
            category="spot",
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        data = response.get("result", {}).get("list", [])

        if not data:
            return pd.DataFrame()

        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', '_1', '_2'
        ])

        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        # تحويل الأنواع
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df[['open', 'high', 'low', 'close', 'volume']] = df[[
            'open', 'high', 'low', 'close', 'volume']].astype(float)

        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)

        return df

    except Exception as e:
        logging.error(f"[fetch_klines] Error fetching {symbol}: {e}")
        return pd.DataFrame()
