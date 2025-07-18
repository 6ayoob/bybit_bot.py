import os
import time
import logging
import pandas as pd
import ta
from pybit import HTTP
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("tLgcha0kFzPnjIKGhQ")
API_SECRET = os.getenv("YMeUOTHgyP59msCjxDfR0qAdHiCKJTo6ePSn")
USE_TESTNET = os.getenv("bot", "False").lower() == "true"

ENDPOINT = "https://api-testnet.bybit.com" if bot else "https://api.bybit.com"
client = HTTP(ENDPOINT, api_key=API_KEY, api_secret=API_SECRET)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bybit_bot.log"), logging.StreamHandler()]
)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
INTERVAL = "15"
RISK_PERCENTAGE = 0.01
STOP_LOSS_PERCENT = 0.01
TAKE_PROFIT_PERCENT = 0.02

def fetch_ohlc(symbol, interval=INTERVAL, limit=200):
    try:
        resp = client.query_kline(symbol=symbol, interval=interval, limit=limit)
        data = resp['result']
        df = pd.DataFrame(data)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='s')
        df.set_index('open_time', inplace=True)
        df = df.astype(float)
        return df
    except Exception as e:
        logging.error(f"خطأ في جلب بيانات {symbol}: {e}")
        return None

def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['macd_diff'] = macd.macd_diff()
    df['ema50'] = ta.trend.EMAIndicator(df['close'], window=50).ema_indicator()
    df['ema200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
    df['volume_ma20'] = df['volume'].rolling(window=20).mean()
    return df

def get_position(symbol):
    try:
        pos = client.my_position(symbol=symbol)
        if pos['result']:
            size = float(pos['result'][0]['size'])
            side = pos['result'][0]['side']
            if size > 0:
                return "long" if side.lower() == "buy" else "short"
        return None
    except Exception as e:
        logging.error(f"خطأ في جلب وضعية الصفقة لـ {symbol}: {e}")
        return None

def calculate_order_quantity(symbol, stop_loss_price, entry_price):
    try:
        balance_data = client.get_wallet_balance(coin="USDT")
        usdt_balance = float(balance_data['result']['USDT']['available_balance'])
        risk_amount = usdt_balance * RISK_PERCENTAGE
        stop_loss_diff = abs(entry_price - stop_loss_price)
        quantity = risk_amount / stop_loss_diff
        quantity = round(quantity, 3)
        if quantity <= 0:
            quantity = 0.001
        return quantity
    except Exception as e:
        logging.error(f"خطأ في حساب كمية التداول: {e}")
        return 0.001

def signal_generator(df, current_position):
    last = df.iloc[-1]
    if last['adx'] < 20:
        return "hold"
    if current_position != "long":
        if (
            last['rsi'] < 30 and
            last['macd'] > last['macd_signal'] and
            last['close'] > last['ema50'] and
            last['volume'] > last['volume_ma20']
        ):
            return "buy"
    if current_position != "short":
        if (
            last['rsi'] > 70 and
            last['macd'] < last['macd_signal'] and
            last['close'] < last['ema50'] and
            last['volume'] > last['volume_ma20']
        ):
            return "sell"
    return "hold"

def place_order(symbol, side, qty, entry_price):
    try:
        order_resp = client.place_active_order(
            symbol=symbol,
            side=side.capitalize(),
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )
        logging.info(f"تم تنفيذ أمر {side} على {symbol}: {order_resp}")

        if side.lower() == "buy":
            stop_loss_price = entry_price * (1 - STOP_LOSS_PERCENT)
            take_profit_price = entry_price * (1 + TAKE_PROFIT_PERCENT)
            sl_side = "Sell"
        else:
            stop_loss_price = entry_price * (1 + STOP_LOSS_PERCENT)
            take_profit_price = entry_price * (1 - TAKE_PROFIT_PERCENT)
            sl_side = "Buy"

        sl_order = client.place_active_order(
            symbol=symbol,
            side=sl_side,
            order_type="Stop",
            qty=qty,
            price=round(stop_loss_price, 2),
            base_price=entry_price,
            stop_px=round(stop_loss_price, 2),
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=True
        )

        tp_order = client.place_active_order(
            symbol=symbol,
            side=sl_side,
            order_type="Limit",
            qty=qty,
            price=round(take_profit_price, 2),
            time_in_force="GoodTillCancel",
            reduce_only=True,
            close_on_trigger=True
        )

        logging.info(f"تم وضع وقف خسارة وأخذ ربح على {symbol}:\nSL: {sl_order}\nTP: {tp_order}")
        return True
    except Exception as e:
        logging.error(f"فشل في تنفيذ أمر {side} على {symbol}: {e}")
        return False

def main():
    logging.info("بدء تشغيل بوت التداول التلقائي على Bybit (حقيقي)...")

    while True:
        for symbol in SYMBOLS:
            current_pos = get_position(symbol)
            df = fetch_ohlc(symbol)
            if df is None:
                logging.warning(f"فشل في جلب بيانات {symbol}")
                continue
            df = add_indicators(df)
            signal = signal_generator(df, current_pos)
            logging.info(f"{symbol} - الإشارة: {signal} - الوضع الحالي: {current_pos}")

            if signal in ["buy", "sell"]:
                last_close = df.iloc[-1]['close']
                stop_loss_price = last_close * (1 - STOP_LOSS_PERCENT if signal=="buy" else 1 + STOP_LOSS_PERCENT)
                qty = calculate_order_quantity(symbol, stop_loss_price=stop_loss_price, entry_price=last_close)
                if qty < 0.001:
                    logging.warning(f"الكمية محسوبة صغيرة جداً لـ {symbol}, تخطي هذه الصفقة")
                    continue
                if current_pos == signal:
                    logging.info(f"الصفقة على {symbol} موجودة بالفعل، تخطي فتح صفقة جديدة")
                    continue
                placed = place_order(symbol, signal, qty, last_close)
                if placed:
                    logging.info(f"تم فتح صفقة {signal} على {symbol} بكمية {qty}")
            else:
                logging.info(f"{symbol} - لا توجد إشارة تنفيذ")

        logging.info(f"انتظار {INTERVAL} دقيقة حتى الجولة القادمة...")
        time.sleep(int(INTERVAL) * 60)

if __name__ == "__main__":
    main()
