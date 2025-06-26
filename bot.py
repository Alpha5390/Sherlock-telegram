import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from username_checker import check_username

BOT_TOKEN = "8095002687:AAEiOMd4nAulyIn0r7kFegeZr6d5WbL8QSA"
CHANNEL_USERNAME = "@V1RU5_team"

POPULAR_SITES = ["Instagram", "GitHub", "Twitter", "Reddit"]

# 🔹 1. Boshlanish
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await is_subscribed(update, context, user_id):
        await prompt_subscription(update)
        return

    keyboard = [
        [InlineKeyboardButton("🌐 Instagram", callback_data="search_Instagram"),
         InlineKeyboardButton("💻 GitHub", callback_data="search_GitHub")],
        [InlineKeyboardButton("🐦 Twitter", callback_data="search_Twitter"),
         InlineKeyboardButton("🗂 Reddit", callback_data="search_Reddit")],
        [InlineKeyboardButton("🔎 Barchasi", callback_data="search_all")]
    ]
    await update.message.reply_text(
        "🕵️‍♂️ Username qidiruvchi bot\n\n👇 Qaysi sayt(lar)da qidirishni xohlaysiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔹 2. Help bo‘limi
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Yordam bo‘limi:\nBu yerga keyinchalik qo‘llanma yozasiz.")

# 🔹 3. Inline tugma bosilganda
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not await is_subscribed(update, context, query.from_user.id):
        await prompt_subscription(update)
        return

    data = query.data
    site = data.replace("search_", "")
    context.user_data["search_target"] = site
    await query.edit_message_text(f"📝 Username yuboring (masalan: johndoe)")

# 🔹 4. Username yuborilganda
async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    site = context.user_data.get("search_target")

    if not await is_subscribed(update, context, update.effective_user.id):
        await prompt_subscription(update)
        return

    if not username:
        await update.message.reply_text("⚠️ Username yuboring.")
        return

    await update.message.reply_text(f"🔍 Tekshirilmoqda: {username}")

    results, found, not_found, errors = await check_username(username, show_progress=False)

    if site != "all":
        found = [r for r in found if r['site'] == site]
        not_found = [r for r in not_found if r['site'] == site]

    if found:
        buttons = []
        row = []
        for r in found:
            row.append(InlineKeyboardButton(r['site'], url=r['url']))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        await update.message.reply_text("✅ Topildi:", reply_markup=InlineKeyboardMarkup(buttons))

    if not_found:
        msg = "❌ Topilmadi:\n" + "\n".join(f"• {r['site']}" for r in not_found)
        await update.message.reply_text(msg)

    if errors:
        msg = "⚠️ Xatoliklar:\n" + "\n".join(f"• {r['site']} - {r['error']}" for r in errors)
        await update.message.reply_text(msg)

# 🔹 5. Obuna tekshiruvi
async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "creator", "administrator"]
    except:
        return False

async def prompt_subscription(update: Update):
    text = f"❗ Botdan foydalanish uchun {CHANNEL_USERNAME} kanaliga obuna bo‘ling."
    button = InlineKeyboardMarkup([[InlineKeyboardButton("🔔 Obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")]])
    if update.message:
        await update.message.reply_text(text, reply_markup=button)
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=button)

# 🔹 6. Botni ishga tushirish
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.run_polling()

if __name__ == "__main__":
    main()
