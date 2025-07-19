# telegram_bot.py

import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# تحميل المتغيرات من .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPEN_POSITIONS_FILE = "open_positions.json"

# أوامر البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 مرحبًا بك! استخدم /help لرؤية الأوامر المتاحة.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = """
📘 أوامر البوت:
/start - بدء المحادثة
/help - قائمة الأوامر
/status - حالة البوت
/positions - الصفقات المفتوحة
/stop - إيقاف البوت مؤقتًا (قيد التطوير)
/resume - استئناف البوت (قيد التطوير)
"""
    await update.message.reply_text(commands)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ البوت يعمل بشكل طبيعي الآن.")

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(OPEN_POSITIONS_FILE):
        with open(OPEN_POSITIONS_FILE, "r") as f:
            positions = json.load(f)

        if positions:
            msg = "📊 الصفقات المفتوحة:\n\n"
            for pos in positions:
                msg += f"• {pos['symbol']} | 📥 الكمية: {pos['quantity']} | 💰 الدخول: {pos['entry_price']}\n"
        else:
            msg = "🚫 لا توجد أي صفقات مفتوحة حالياً."
    else:
        msg = "🚫 لم يتم العثور على ملف الصفقات."

    await update.message.reply_text(msg)

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 تم إيقاف البوت مؤقتًا (قيد التطوير).")

async def resume_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("▶️ تم استئناف تشغيل البوت (قيد التطوير).")

def run_telegram_bot():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ خطأ: لم يتم تعيين TELEGRAM_BOT_TOKEN في ملف .env")
        return

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("positions", positions))
    application.add_handler(CommandHandler("stop", stop_bot))
    application.add_handler(CommandHandler("resume", resume_bot))

    print("🤖 Telegram Bot is now running...")
    application.run_polling()

# التأكد من عدم تشغيل البوت عند الاستيراد
if name == "__main__":
    run_telegram_bot()
