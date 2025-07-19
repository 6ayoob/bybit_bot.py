# telegram_bot.py

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from trader import load_open_positions

BOT_TOKEN = "7800699278:AAEdMakvUEwysq-s0k9MsK6k4b4ucyHRfT4"

ALLOWED_USERS = [658712542]  # غيّر المعرف إلى معرفك

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return await update.message.reply_text("🚫 غير مصرح لك باستخدام هذا البوت.")
    await update.message.reply_text("✅ البوت يعمل ومتصِل!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return await update.message.reply_text("🚫 غير مصرح لك باستخدام هذا البوت.")
    positions = load_open_positions()
    if not positions:
        await update.message.reply_text("لا توجد صفقات مفتوحة حالياً.")
    else:
        msg = ""
        for pos in positions:
            msg += f"🔹 {pos['symbol']} - كمية: {pos['quantity']}, الدخول: {pos['entry_price']}, SL: {pos['stop_loss']}, TP: {pos['take_profit']}\n"
        await update.message.reply_text(f"📊 الصفقات المفتوحة:\n{msg}")

def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    logging.info("📲 بوت التليجرام جاهز.")
    app.run_polling()
