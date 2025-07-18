from flask import Flask
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

app = Flask(__name__)

def trading_bot_job():
    print("تشغيل البوت... تحليل وتنفيذ أوامر التداول")
    # مثال: run_trading_strategy()

scheduler = BackgroundScheduler()
scheduler.add_job(trading_bot_job, 'interval', minutes=1)
scheduler.start()

@app.route('/')
def index():
    return "بوت التداول يعمل بنجاح!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # 🔁 هذا هو التعديل المهم
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()

    while True:
        time.sleep(1)
