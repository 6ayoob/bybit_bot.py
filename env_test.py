import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من .env
load_dotenv()

# طباعة القيم للتأكد من أنها ليست None
print("BYBIT_API_KEY:", os.getenv("BYBIT_API_KEY"))
print("BYBIT_API_SECRET:", os.getenv("BYBIT_API_SECRET"))
print("BOT_TOKEN:", os.getenv("BOT_TOKEN"))
print("CHAT_ID:", os.getenv("CHAT_ID"))
print("POSITION_TRACKER_FILE:", os.getenv("POSITION_TRACKER_FILE"))
print("CAPITAL:", os.getenv("CAPITAL"))
print("RISK_PERCENT:", os.getenv("RISK_PERCENT"))
