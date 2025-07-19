from pybit.unified_trading import HTTP
from ta.volatility import average_true_range
import pandas as pd
import logging
from utils import fetch_klines

# إعداد جلسة pybit
session = HTTP(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET", testnet=False)

# رأس المال الكلي بالدولار
CAPITAL = 1000
RISK_PERCENT = 0.02  # مخاطرة 2% من رأس المال لكل صفقة

def calculate_position_size(df: pd.DataFrame, symbol: str) -> tuple:
    """
    حساب حجم الصفقة ووقف الخسارة باستخدام ATR
    """
    atr = average_true_range(df['high'], df['low'], df['close'], window=14)
    latest_atr = atr.iloc[-1]

    latest_price = df['close'].iloc[-1]
    stop_loss_price = latest_price - (1.5 * latest_atr)  # SL تحت السعر الحالي بـ 1.5x ATR
    risk_amount = CAPITAL * RISK_PERCENT
    quantity = risk_amount / (latest_price - stop_loss_price)

    return round(quantity, 4), round(stop_loss_price, 4)


def execute_trade(symbol: str):
    """
    تنفيذ صفقة شراء بـ وقف خسارة بناءً على الإشارة
    """
    try:
        df = fetch_klines(symbol, interval='30m', limit=100)
        if df.empty:
            print(f"{symbol} - لا توجد بيانات")
            return

        quantity, stop_loss = calculate_position_size(df, symbol)
        current_price = df['close'].iloc[-1]

        # تنفيذ أمر Market Buy
        buy_order = session.place_order(
            category="spot",
            symbol=symbol,
            side="Buy",
            order_type="Market",
            qty=quantity
        )

        print(f"✅ شراء {symbol} - الكمية: {quantity} - السعر الحالي: {current_price}")

        # ملاحظة: Bybit Spot لا يدعم SL مباشر، لذا تحتاج إلى متابعة السعر يدويًا أو برمجيًا لاحقًا
        print(f"🚨 وقف الخسارة المقترح: {stop_loss}")

        # يمكن مستقبلاً تنفيذ البيع التلقائي عند تحقق شرط وقف الخسارة أو جني الأرباح
        return buy_order

    except Exception as e:
        logging.error(f"[execute_trade] خطأ في {symbol}: {e}")
        return None
