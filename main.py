import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# =======================
# TOKEN
# =======================
TOKEN = os.getenv("TOKEN")

# =======================
# DATABASE
# =======================
conn = sqlite3.connect("bot.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS tickets (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT,
username TEXT,
message TEXT
)
""")

conn.commit()

# =======================
# STATES
# =======================
SUPPORT = 1

# =======================
# START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍 المنتجات", callback_data="products")],
        [InlineKeyboardButton("🎫 الدعم الفني", callback_data="support")],
        [InlineKeyboardButton("📦 طلباتي", callback_data="orders")]
    ]

    await update.message.reply_text(
        "👋 مرحباً بك في SITQOR STORE\n\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =======================
# MENU HANDLER
# =======================
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "products":
        await q.message.reply_text("🛍 المنتجات قيد التطوير...")

    elif q.data == "orders":
        await q.message.reply_text("📦 لا توجد طلبات حالياً")

    elif q.data == "support":
        await q.message.reply_text(
            "🎫 الدعم الفني\n\n"
            "اكتب مشكلتك الآن وسيتم الرد عليك قريباً 👇"
        )
        return SUPPORT

# =======================
# SUPPORT SAVE
# =======================
async def support_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    cur.execute(
        "INSERT INTO tickets (user_id, username, message) VALUES (?, ?, ?)",
        (str(user.id), user.username, update.message.text)
    )
    conn.commit()

    await update.message.reply_text("✅ تم استلام تذكرتك بنجاح")
    return ConversationHandler.END

# =======================
# APP
# =======================
app = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(menu)],
    states={
        SUPPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_msg)]
    },
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(conv)

app.run_polling()
