import logging
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from scanner import analyze_coin
from trader import execute_trade, monitor_positions
from telegram_bot import send_message, run_telegram_bot

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
    logging.info("✅ تم بدء جدولة فحص العملات كل 30 دقيقة.")

    # تشغيل مراقبة الصفقات المفتوحة في ثريد منفصل مع حلقة دائمة
    monitor_thread = threading.Thread(target=monitor_positions, kwargs={'sleep_seconds': 10}, daemon=True)
    monitor_thread.start()
    logging.info("✅ تم بدء مراقبة الصفقات المفتوحة في ثريد مستقل.")

    # تشغيل بوت التليجرام في ثريد مستقل
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    logging.info("✅ تم تشغيل بوت التليجرام في ثريد مستقل.")

    # إبقاء البرنامج شغالًا
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logging.info("إيقاف البوت...")
        scheduler.shutdown()
