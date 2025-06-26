import asyncio, json, os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from username_checker import check_username

BOT_TOKEN = "8095002687:AAEiOMd4nAulyIn0r7kFegeZr6d5WbL8QSA"
ADMIN_ID = ['6510338337','7935854444']  # o'zingizning Telegram ID'ingiz

STATS_FILE = "database.json"

def load_stats():
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, "w") as f:
            json.dump({"users": [], "total_checks": 0}, f)
    with open(STATS_FILE, "r") as f:
        return json.load(f)

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Salom! Username tekshiruvchi botga xush kelibsiz!\n\n"
        "Yuboring: `username`\nNatijalar inline tugmalar orqali chiqadi.",
        parse_mode="Markdown"
    )

async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()

    if not username.isalnum():
        await update.message.reply_text("⚠️ Iltimos, faqat harf va raqamdan iborat foydalanuvchi nom yuboring.")
        return

    # statistikaga yozish
    stats = load_stats()
    if update.effective_user.id not in stats["users"]:
        stats["users"].append(update.effective_user.id)
    stats["total_checks"] += 1
    save_stats(stats)

    await update.message.reply_text(
        f"🔍 `{username}` username tekshirildi.\nNatijani quyidan tanlang:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔝 Top 4", callback_data=f"top4|{username}")],
            [InlineKeyboardButton("🧾 Hammasi", callback_data=f"all|{username}")],
            [InlineKeyboardButton("🔁 Qayta tekshir", callback_data=f"check|{username}")]
        ])
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, username = query.data.split("|")

    results, found, not_found, errors = await check_username(username, show_progress=False)

    if action == "top4":
        top = found[:4]
        if top:
            text = "🔝 *Top 4 ta topilgan natija:*\n" + "\n".join(
                [f"[{r['site']}]({r['url']})" for r in top]
            )
        else:
            text = "❌ Hech narsa topilmadi."
        await query.edit_message_text(text=text, parse_mode="Markdown")

    elif action == "all":
        if found:
            text = "🧾 *Barcha topilganlar:*\n" + "\n".join(
                [f"[{r['site']}]({r['url']})" for r in found]
            )
        else:
            text = "❌ Hech narsa topilmadi."
        await query.edit_message_text(text=text, parse_mode="Markdown")

    elif action == "check":
        await query.edit_message_text(text="🔄 Qayta tekshirilmoqda...")
        results, found, _, _ = await check_username(username, show_progress=False)
        if found:
            msg = "✅ *Topildi:*\n" + "\n".join([f"[{r['site']}]({r['url']})" for r in found])
        else:
            msg = "❌ *Hech narsa topilmadi.*"
        await query.edit_message_text(text=msg, parse_mode="Markdown")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 Siz admin emassiz.")
        return

    stats = load_stats()
    total = stats.get("total_checks", 0)
    users = len(stats.get("users", []))

    await update.message.reply_text(
        f"👨‍💻 *Admin Panel*\n\n"
        f"👤 Foydalanuvchilar: `{users}`\n"
        f"🔍 Umumiy tekshiruvlar: `{total}`",
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
