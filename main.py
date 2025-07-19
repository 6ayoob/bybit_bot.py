import logging
from apscheduler.schedulers.background import BackgroundScheduler
from scanner import analyze_coin
from trader import execute_trade, monitor_positions
from telegram_bot import send_message, run_telegram_bot
import threading
import time

coins_list = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
    "SOLUSDT", "DOGEUSDT", "TONUSDT", "DOTUSDT", "AVAXUSDT",
    "TRXUSDT", "MATICUSDT", "LINKUSDT", "ICPUSDT", "LTCUSDT",
    "SHIBUSDT", "BCHUSDT", "NEARUSDT", "UNIUSDT", "XLMUSDT"
]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("📈 بدء فحص العملات...")
    for symbol in coins_list:
        try:
            signal = analyze_coin(symbol)
            if signal:
                logging.info(f"📌 إشارة شراء على {symbol}, يتم التنفيذ...")
                order = execute_trade(symbol)
                if order:
                    send_message(f"✅ تم شراء {symbol} بنجاح.")
                else:
                    send_message(f"⚠️ فشل تنفيذ الصفقة على {symbol}.")
            else:
                logging.info(f"✖️ لا توجد إشارة على {symbol}")
        except Exception as e:
            logging.error(f"🚨 خطأ في تحليل أو تنفيذ {symbol}: {e}")
            send_message(f"❌ خطأ في البوت على {symbol}: {e}")
    logging.info("✅ انتهاء الفحص.")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', minutes=30)
    scheduler.start()
    logging.info("✅ تم بدء جدولة المهام.")

    monitor_thread = threading.Thread(target=monitor_positions, daemon=True)
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)

    monitor_thread.start()
    telegram_thread.start()

    logging.info("✅ تم تشغيل مراقبة الصفقات وبوت التليجرام في الخلفية.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("⏹️ تم إيقاف البرنامج.")
