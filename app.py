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
    # هنا ضع كود التداول الخاص بك
    print("تشغيل البوت... تحليل وتنفيذ أوامر التداول")

    # مثال: هنا تضع استدعاء دوال استراتيجيتك، مثلاً:
    # run_trading_strategy()

scheduler = BackgroundScheduler()
scheduler.add_job(trading_bot_job, 'interval', minutes=1)
scheduler.start()

@app.route('/')
def index():
    return "بوت التداول يعمل بنجاح!"

if __name__ == "__main__":
    # تشغيل Flask في Thread منفصل حتى تبقى جدولة المهام تعمل
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

    # إبقاء البرنامج شغال
    while True:
        time.sleep(1)
