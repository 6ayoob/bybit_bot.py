import os
import json
import time
import requests
import pandas as pd
import ta
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from pybit.spot import HTTP
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("tLgcha0kFzPnjIKGhQ")
API_SECRET = os.getenv("YMeUOTHgyP59msCjxDfR0qAdHiCKJTo6ePSn")
USE_TESTNET = os.getenv("USE_TESTNET", "False").lower() == "true"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
RISK_PERCENT = float(os.getenv("RISK_PERCENT", 10))
POSITION_TRACKER_FILE = os.getenv("POSITION_TRACKER_FILE", "positions.json")

ENDPOINT = "https://api-testnet.bybit.com" if USE_TESTNET else "https://api.bybit.com"
client = HTTP(ENDPOINT, api_key=API_KEY, api_secret=API_SECRET)
bot = Bot(token=BOT_TOKEN)

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
    try:
        balance_data = client.get_wallet_balance()
        return float(balance_data.get('result', {}).get('USDT', {}).get('availableBalance', 0))
    except Exception as e:
        print(f"Error fetching balance: {e}")
        return 0

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

def get_klines(symbol, interval='1h', limit=100):
    url = "https://api.bybit.com/spot/quote/v1/kline"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('ret_code') != 0:
            print(f"API error: {data.get('ret_msg')}")
            return None
        df = pd.DataFrame(data['result'])
        if df.empty:
            return None
        df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume']
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
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

    if pd.isna(latest['ema9']) or pd.isna(latest['ema21']) or pd.isna(latest['rsi']):
        return None

    if latest['ema9'] > latest['ema21'] and latest['rsi'] < 30:
        return "Buy"
    elif latest['ema9'] < latest['ema21'] and latest['rsi'] > 70:
        return "Sell"
    return None

def manage_risk_and_place_order(symbol, side, entry_price, sl_price, tp_price):
    positions = load_positions()
    if symbol in positions:
        print(f"صفقة مفتوحة مسبقًا لـ {symbol}, تخطي.")
        return

    balance = get_account_balance()
    if balance == 0:
        print("رصيد الحساب صفر، لا يمكن فتح صفقة.")
        return

    trade_value = balance * (RISK_PERCENT / 100)
    qty = round(trade_value / entry_price, 6)

    if qty <= 0:
        print(f"الكمية المحسوبة ل {symbol} غير صالحة: {qty}")
        return

    try:
        order = client.place_order(
            symbol=symbol,
            side=side,
            orderType="MARKET",
            qty=str(qty)
        )
        if order.get('ret_code') != 0:
            print(f"خطأ في تنفيذ الطلب: {order.get('ret_msg')}")
            send_telegram_message(f"❌ فشل تنفيذ الطلب لـ {symbol}: {order.get('ret_msg')}")
            return

        order_id = order['result'].get('orderId', 'N/A')
        positions[symbol] = {
            "side": side,
            "qty": qty,
            "entry_price": entry_price,
            "sl": sl_price,
            "tp": tp_price,
            "order_id": order_id
        }
        save_positions(positions)

        send_telegram_message(
            f"📈 صفقة جديدة: {symbol}\nالاتجاه: {side}\nالكمية: {qty}\nالسعر: {entry_price}\nوقف الخسارة: {sl_price}\nجني الأرباح: {tp_price}"
        )
        print(f"تم فتح صفقة {side} على {symbol} بكمية {qty}")
    except Exception as e:
        print(f"Order error: {e}")
        send_telegram_message(f"❌ فشل تنفيذ الصفقة لـ {symbol}: {e}")

def trading_job():
    print("🔄 بدء الفحص الدوري...")
    top_symbols = get_top_spot_symbols()
    if not top_symbols:
        print("لا توجد رموز للتداول.")
        return
    for symbol in top_symbols:
        signal = should_enter_trade(symbol)
        if signal:
            df = get_klines(symbol)
            if df is None or df.empty:
                continue
            price = float(df.iloc[-1]['close'])
            sl = round(price * 0.98, 6) if signal == "Buy" else round(price * 1.02, 6)
            tp = round(price * 1.03, 6) if signal == "Buy" else round(price * 0.97, 6)
            manage_risk_and_place_order(symbol, signal, price, sl, tp)
        else:
            print(f"لا توجد إشارة تداول لـ {symbol}")
    print("✅ تم تنفيذ المهمة.")

if __name__ == "__main__":
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Riyadh'))
    scheduler.add_job(trading_job, 'interval', minutes=30)
    scheduler.start()
    send_telegram_message("✅ بوت التداول بدأ العمل ✅")
    print("🤖 تم تشغيل البوت بنجاح. يعمل كل 30 دقيقة...")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("إيقاف البوت...")
        scheduler.shutdown()
