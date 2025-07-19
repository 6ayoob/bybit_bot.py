import json
import os
import logging
from risk_manager import RiskManager
from utils import fetch_klines
from pybit.unified_trading import HTTP
from telegram_bot import send_message

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
session = HTTP(api_key=API_KEY, api_secret=API_SECRET, testnet=False)

CAPITAL = 1000
RISK_PERCENT = 0.02
risk_manager = RiskManager(capital=CAPITAL, risk_percent=RISK_PERCENT)

OPEN_POSITIONS_FILE = "open_positions.json"

def save_open_position(position_data):
    positions = []
    if os.path.exists(OPEN_POSITIONS_FILE):
        with open(OPEN_POSITIONS_FILE, "r") as f:
            positions = json.load(f)
    positions.append(position_data)
    with open(OPEN_POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def load_open_positions():
    if os.path.exists(OPEN_POSITIONS_FILE):
        with open(OPEN_POSITIONS_FILE, "r") as f:
            return json.load(f)
    return []

def remove_position(symbol):
    positions = load_open_positions()
    positions = [pos for pos in positions if pos['symbol'] != symbol]
    with open(OPEN_POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

def execute_trade(symbol: str, take_profit_multiplier=3):
    try:
        df = fetch_klines(symbol, interval='30m', limit=100)
        if df.empty:
            logging.warning(f"{symbol} - لا توجد بيانات كافية")
            return

        current_price = df['close'].iloc[-1]
        quantity, stop_loss = risk_manager.calculate_position_size(df, current_price)
        if quantity == 0:
            logging.warning(f"{symbol} - حجم الصفقة المحسوب صفر، تخطي التنفيذ")
            return

        buy_order = session.place_order(
            category="spot",
            symbol=symbol,
            side="Buy",
            order_type="Market",
            qty=quantity
        )

        take_profit = current_price + take_profit_multiplier * (current_price - stop_loss)

        position_data = {
            "symbol": symbol,
            "quantity": quantity,
            "entry_price": current_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit
        }

        save_open_position(position_data)

        message = (
            f"✅ *تم فتح صفقة شراء*\n"
            f"🔹 العملة: {symbol}\n"
            f"🔹 الكمية: {quantity}\n"
            f"💰 السعر: {current_price:.4f}\n"
            f"🚨 وقف الخسارة: {stop_loss:.4f}\n"
            f"🎯 جني الربح: {take_profit:.4f}"
        )
        send_message(message)

        return buy_order

    except Exception as e:
        logging.error(f"[execute_trade] خطأ في {symbol}: {e}")
        send_message(f"❌ خطأ في تنفيذ صفقة على {symbol}:\n{e}")
        return None

def monitor_positions():
    positions = load_open_positions()
    for pos in positions:
        symbol = pos['symbol']
        quantity = pos['quantity']
        stop_loss = pos['stop_loss']
        take_profit = pos['take_profit']

        df = fetch_klines(symbol, interval='1m', limit=1)
        if df.empty:
            continue

        current_price = df['close'].iloc[-1]

        if current_price <= stop_loss:
            session.place_order(
                category="spot",
                symbol=symbol,
                side="Sell",
                order_type="Market",
                qty=quantity
            )
            send_message(
                f"🛑 *تم إغلاق الصفقة بوقف الخسارة*\n"
                f"🔹 العملة: {symbol}\n"
                f"💰 السعر: {current_price:.4f}"
            )
            remove_position(symbol)

        elif current_price >= take_profit:
            session.place_order(
                category="spot",
                symbol=symbol,
                side="Sell",
                order_type="Market",
                qty=quantity
            )
            send_message(
                f"🎯 *تم جني الربح وإغلاق الصفقة*\n"
                f"🔹 العملة: {symbol}\n"
                f"💰 السعر: {current_price:.4f}"
            )
            remove_position(symbol)
