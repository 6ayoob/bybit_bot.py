from flask import Flask
import threading
import time
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "بوت التداول يعمل بنجاح!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()

    while True:
        time.sleep(1)
