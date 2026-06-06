import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters

# 🔴 ضع التوكن هنا
TOKEN = 8745145806:AAEVMLDgVWwPqGFSI6_MQr3WK3QE243su6Q

# DATABASE
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

# STATES
SUPPORT = 1

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🛍 المنتجات", callback_data="products")],
        [InlineKeyboardButton("🎫 الدعم الفني", callback_data="support")]
    ]

    await update.message.reply_text(
        "👋 مرحباً بك في SITQOR STORE\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# MENU
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "products":
        await q.message.reply_text("🛍 المنتجات قيد التطوير...")

    elif q.data == "support":
        await q.message.reply_text("🎫 اكتب مشكلتك الآن 👇")
        return SUPPORT

# SUPPORT SAVE
async def support_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user

    cur.execute(
        "INSERT INTO tickets (user_id, username, message) VALUES (?, ?, ?)",
        (str(user.id), user.username, update.message.text)
    )
    conn.commit()

    await update.message.reply_text("✅ تم استلام تذكرتك بنجاح")
    return ConversationHandler.END

# APP
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
