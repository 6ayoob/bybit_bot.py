from risk_manager import RiskManager
from utils import fetch_klines
from pybit.unified_trading import HTTP
import logging

# إعداد جلسة Bybit Spot (ضع مفاتيحك هنا)
API_KEY = "tLgcha0kFzPnjIKGhQ"
API_SECRET = "YMeUOTHgyP59msCjxDfR0qAdHiCKJTo6ePSn"
session = HTTP(api_key=API_KEY, api_secret=API_SECRET, testnet=False)

# إعداد رأس المال ونسبة المخاطرة
CAPITAL = 1000
RISK_PERCENT = 0.02

risk_manager = RiskManager(capital=CAPITAL, risk_percent=RISK_PERCENT)

def execute_trade(symbol: str):
    """
    تنفيذ صفقة شراء مع حساب حجم الصفقة ووقف الخسارة باستخدام RiskManager
    """
    try:
        df = fetch_klines(symbol, interval='30m', limit=100)
        if df.empty:
            logging.warning(f"{symbol} - لا توجد بيانات كافية")
            return

        current_price = df['close'].iloc[-1]

        # حساب حجم الصفقة ووقف الخسارة
        quantity, stop_loss = risk_manager.calculate_position_size(df, current_price)

        if quantity == 0:
            logging.warning(f"{symbol} - حجم الصفقة المحسوب صفر، تخطي التنفيذ")
            return

        # تنفيذ أمر شراء Market
        buy_order = session.place_order(
            category="spot",
            symbol=symbol,
            side="Buy",
            order_type="Market",
            qty=quantity
        )

        logging.info(f"✅ تم شراء {symbol} كمية {quantity} بسعر {current_price}")
        logging.info(f"🚨 وقف الخسارة المقترح: {stop_loss}")

        return buy_order

    except Exception as e:
        logging.error(f"[execute_trade] خطأ في {symbol}: {e}")
        return None
