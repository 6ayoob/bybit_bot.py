import os
import json
import time
import requests
import pandas as pd
import ta
from apscheduler.schedulers.background import BackgroundScheduler
from pybit import HTTP
from telegram import Bot

# ------------------ الإعدادات ------------------
API_KEY = "tLgcha0kFzPnjIKGhQ"
API_SECRET = "YMeUOTHgyP59msCjxDfR0qAdHiCKJTo6ePSn"
BOT_TOKEN = "7800699278:AAEdMakvUEwysq-s0k9MsK6k4b4ucyHRfT4"
CHAT_ID = 658712542  # استبدله بمعرف التيليجرام الخاص بك
RISK_PERCENT = 10  # نسبة المخاطرة من رأس المال
POSITION_TRACKER_FILE = "489727585"
client = HTTP("https://api.bybit.com", api_key=API_KEY, api_secret=API_SECRET)
bot = Bot(token=BOT_TOKEN)

# ------------------ وظائف مساعدة ------------------

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
    except Exception as e:
        print(f"Telegram error: {e}")

def load_positions():
    if os.path.exists(POSITION_TRACKER_FILE):
        with open(POSITION_TRACKER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_positions(positions):
    with open(POSITION_TRACKER_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def get_account_balance():
    balance_data = client.get_wallet_balance()
    return float(balance_data.get('result', {}).get('USDT', {}).get('available_balance', 0))

# ------------------ 1: جلب أعلى العملات ------------------

def get_top_spot_symbols():
    url = "https://api.bybit.com/spot/v1/tickers"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        tickers = data.get('result', [])
        volume_data = []

        for ticker in tickers:
            symbol = ticker.get('symbol')
            try:
                volume = float(ticker.get('volume', 0))
                volume_data.append({'symbol': symbol, 'volume': volume})
            except:
                continue

        volume_data.sort(key=lambda x: x['volume'], reverse=True)
        return [item['symbol'] for item in volume_data[:5]]
    except Exception as e:
        print(f"Volume fetch error: {e}")
        return []

# ------------------ 2: تحليل EMA + RSI ------------------

def get_klines(symbol, interval='1h', limit=100):
    url = "https://api.bybit.com/spot/quote/v1/kline"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['result'])
        df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        df['close'] = pd.to_numeric(df['close'])
        return df
    except Exception as e:
        print(f"Klines error for {symbol}: {e}")
        return None

def should_enter_trade(symbol):
    df = get_klines(symbol)
    if df is None or df.empty:
        return None

    df['ema9'] = ta.trend.ema_indicator(df['close'], window=9)
    df['ema21'] = ta.trend.ema_indicator(df['close'], window=21)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    latest = df.iloc[-1]

    if latest['ema9'] > latest['ema21'] and latest['rsi'] < 30:
        return "Buy"
    elif latest['ema9'] < latest['ema21'] and latest['rsi'] > 70:
        return "Sell"
    return None

# ------------------ 3: تنفيذ الصفقة ------------------

def manage_risk_and_place_order(symbol, side, entry_price, sl_price, tp_price):
    positions = load_positions()
    if symbol in positions:
        return  # صفقة مفتوحة مسبقًا

    balance = get_account_balance()
    trade_value = balance * (RISK_PERCENT / 100)
    qty = round(trade_value / entry_price, 6)

    try:
        order = client.place_active_order(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel"
        )
        order_id = order['result']['order_id']
        positions[symbol] = {
            "side": side, "qty": qty,
            "entry_price": entry_price,
            "sl": sl_price,
            "tp": tp_price,
            "order_id": order_id
        }
        save_positions(positions)
        send_telegram_message(f"📈 صفقة جديدة: {symbol}\nالاتجاه: {side}\nالكمية: {qty}\nالسعر: {entry_price}\nSL: {sl_price}\nTP: {tp_price}")
    except Exception as e:
        print(f"Order error: {e}")
        send_telegram_message(f"❌ فشل تنفيذ الصفقة لـ {symbol}: {e}")

# ------------------ 4: المهمة المجدولة ------------------

def trading_job():
    print("🔄 بدء الفحص الدوري...")
    top_symbols = get_top_spot_symbols()
    for symbol in top_symbols:
        signal = should_enter_trade(symbol)
        if signal:
            price = float(get_klines(symbol).iloc[-1]['close'])
            sl = round(price * 0.98, 2) if signal == "Buy" else round(price * 1.02, 2)
            tp = round(price * 1.03, 2) if signal == "Buy" else round(price * 0.97, 2)
            manage_risk_and_place_order(symbol, signal, price, sl, tp)
    print("✅ تم تنفيذ المهمة.")

# ------------------ تشغيل الجدولة ------------------

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(trading_job, 'interval', minutes=30)
    scheduler.start()
    send_telegram_message("✅ بوت التداول بدأ العمل ✅")
    print("🤖 تم تشغيل البوت بنجاح. يعمل كل 30 دقيقة...")

    # إبقاء السكربت شغال دائمًا
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("إيقاف البوت...")
        scheduler.shutdown()
