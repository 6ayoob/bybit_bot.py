import json
import os
from pybit import HTTP

# إعدادات API Bybit Spot - عدلها بمفاتيحك
API_KEY = "tLgcha0kFzPnjIKGhQ"
API_SECRET = "YMeUOTHgyP59msCjxDfR0qAdHiCKJTo6ePSn"
client = HTTP("https://api.bybit.com", api_key=API_KEY, api_secret=API_SECRET)

POSITION_TRACKER_FILE = "position_tracker.json"
RISK_PERCENT = 2  # نسبة 10% من رأس المال

def load_positions():
    if os.path.exists(POSITION_TRACKER_FILE):
        with open(POSITION_TRACKER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_positions(positions):
    with open(POSITION_TRACKER_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def get_account_balance():
    # جلب رصيد العملة الأساسية (مثلاً USDT) من حساب Spot
    balances = client.get_wallet_balance()
    # بافتراض العملة الأساسية USDT
    usdt_balance = float(balances.get('result', {}).get('USDT', {}).get('available_balance', 0))
    return usdt_balance

def manage_risk_and_place_order(symbol, side, entry_price, stop_loss_price, take_profit_price):
    positions = load_positions()

    # منع فتح صفقة إذا كانت موجودة
    if symbol in positions:
        print(f"Position already open for {symbol}. Skipping order.")
        return False

    balance = get_account_balance()
    trade_value = balance * (RISK_PERCENT / 100)  # 10% من الرصيد

    # حساب كمية العملة للشراء/البيع
    # كمية = قيمة الصفقة / سعر الدخول
    qty = trade_value / entry_price

    # تقريب الكمية حسب قواعد السوق (نحتاج تفاصيل دقة الكمية لكل عملة، هنا تقريب بسيط)
    qty = round(qty, 6)

    try:
        # تنفيذ أمر سوق
        order_response = client.place_active_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )
        if order_response.get('ret_code') != 0:
            print(f"Order failed: {order_response.get('ret_msg')}")
            return False

        order_id = order_response['result']['order_id']

        # وضع أوامر وقف خسارة وأخذ ربح منفصلة (لو API يدعمها Spot)
        # Bybit Spot لا يدعم TP/SL أوامر تلقائية في نفس الطلب لكن يمكن إنشاء أوامر مخصصة.
        # هنا مثال لوضع أوامر حدود (Limit) TP و SL:
        # وقف خسارة (Stop Loss) أمر بيع عند سعر أقل من سعر الدخول للشراء والعكس صحيح
        # أخذ ربح (Take Profit) أمر بيع عند سعر أعلى من سعر الدخول للشراء والعكس صحيح

        # أمر وقف خسارة
        sl_order_response = client.place_active_order(
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            order_type="Limit",
            price=stop_loss_price,
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=False
        )
        # أمر أخذ ربح
        tp_order_response = client.place_active_order(
            symbol=symbol,
            side="Sell" if side == "Buy" else "Buy",
            order_type="Limit",
            price=take_profit_price,
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=False
        )

        # تخزين الصفقة المفتوحة في الملف
        positions[symbol] = {
            "side": side,
            "qty": qty,
            "entry_price": entry_price,
            "stop_loss": stop_loss_price,
            "take_profit": take_profit_price,
            "order_id": order_id,
            "sl_order_id": sl_order_response['result']['order_id'] if sl_order_response.get('ret_code') == 0 else None,
            "tp_order_id": tp_order_response['result']['order_id'] if tp_order_response.get('ret_code') == 0 else None
        }
        save_positions(positions)
        print(f"Order placed for {symbol} with qty {qty}")
        return True

    except Exception as e:
        print(f"Error placing order: {e}")
        return False

# مثال استدعاء
if __name__ == "__main__":
    # مثال أسعار (حسب السوق الحقيقي)
    symbol = "BTCUSDT"
    side = "Buy"
    entry_price = 30000
    stop_loss_price = 29500
    take_profit_price = 31000

    manage_risk_and_place_order(symbol, side, entry_price, stop_loss_price, take_profit_price)
