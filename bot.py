# bot.py
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from username_checker import check_username

BOT_TOKEN = "8095002687:AAEiOMd4nAulyIn0r7kFegeZr6d5WbL8QSA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Foydalanuvchi nomini yuboring (masalan: johndoe)")

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    if not username:
        await update.message.reply_text("⚠️ Foydalanuvchi nomi yuboring.")
        return

    await update.message.reply_text(f"🔍 Tekshirilmoqda: {username}")

    results, found, not_found, errors = await check_username(username, show_progress=False)

    if found:
        msg = "✅ Topildi:\n"
        msg += "\n".join([f"• {r['site']}: {r['url']}" for r in found])
        await update.message.reply_text(msg)

    if not_found:
        msg = "❌ Topilmadi:\n"
        msg += "\n".join([f"• {r['site']}" for r in not_found])
        await update.message.reply_text(msg)

    if errors:
        msg = "⚠️ Xatoliklar:\n"
        msg += "\n".join([f"• {r['site']} - {r['error']}" for r in errors])
        await update.message.reply_text(msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.run_polling()

if __name__ == "__main__":
    main()
