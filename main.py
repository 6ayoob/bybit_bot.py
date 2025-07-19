import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from scanner import analyze_coin
from trader import execute_trade, monitor_positions
from telegram_bot import send_message

coins_list = [
    "BTCUSDT", "ETHUSDT", "CFXUSDT", "BNBUSDT", "SOLUSDT",
    "PEPEUSDT", "DOGEUSDT", "STETHUSDT", "TRXUSDT", "ADAUSDT",
    "WBTCUSDT", "LINKUSDT", "AVAXUSDT", "XLMUSDT", "LEOUSDT",
    "TONUSDT", "SHIBUSDT", "BCHUSDT", "LTCUSDT", "FILUSDT"
]

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("🔍 بدء فحص العملات...")

    for symbol in coins_list:
        try:
            signal = analyze_coin(symbol)
            if signal:
                logging.info(f"✅ إشارة شراء على {symbol}، تنفيذ صفقة...")
                order = execute_trade(symbol)
                if order:
                    send_message(f"✅ تم شراء {symbol} بنجاح.")
                else:
                    send_message(f"⚠️ فشل تنفيذ الصفقة على {symbol}.")
            else:
                logging.info(f"⚠️ لا توجد إشارة شراء على {symbol}")
        except Exception as e:
            logging.error(f"❌ خطأ أثناء تحليل أو تنفيذ الصفقة على {symbol}: {e}")
            send_message(f"❌ خطأ في البوت على {symbol}: {e}")

    logging.info("✅ انتهى فحص العملات.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=30)
    scheduler.add_job(monitor_positions, 'interval', minutes=5)
    logging.info("🚀 تم بدء جدولة البوت: فحص العملات كل 30 دقيقة، مراقبة الصفقات كل 5 دقائق.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 تم إيقاف البوت يدويًا.")
