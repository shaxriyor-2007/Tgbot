import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("8261723027:AAFmFL6B-simnFKqXkGSjb4-H28-5h55Kzc")
ADMIN_ID = int(os.getenv("6227666140"))  # o'zingning telegram ID

# Mahsulotlar
PRODUCTS = {
    "iphone": {
        "name": "📱 iPhone 13",
        "price": "7 500 000 so'm"
    },
    "samsung": {
        "name": "📱 Samsung S22",
        "price": "6 200 000 so'm"
    },
    "redmi": {
        "name": "📱 Redmi Note 13",
        "price": "3 200 000 so'm"
    }
}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Mahsulotlar", callback_data="products")],
        [InlineKeyboardButton("📞 Admin bilan aloqa", callback_data="contact")]
    ]
    await update.message.reply_text(
        "👋 Telefon savdo botiga xush kelibsiz!\n\nKerakli bo‘limni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Tugmalar
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "products":
        keyboard = []
        for key, product in PRODUCTS.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{product['name']} - {product['price']}",
                    callback_data=f"buy_{key}"
                )
            ])

        keyboard.append([InlineKeyboardButton("⬅️ Orqaga", callback_data="back")])

        await query.edit_message_text(
            "📦 Mavjud mahsulotlar:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("buy_"):
        product_key = query.data.replace("buy_", "")
        product = PRODUCTS[product_key]

        context.user_data["order"] = product

        await query.edit_message_text(
            f"🛒 Siz tanladingiz:\n\n"
            f"{product['name']}\n"
            f"Narxi: {product['price']}\n\n"
            f"📞 Iltimos, telefon raqamingizni yuboring:"
        )

    elif query.data == "contact":
        await query.edit_message_text(
            "📞 Admin bilan bog‘lanish:\n"
            "@telefonchi_savdogar"
        )

    elif query.data == "back":
        await start(update, context)

# Telefon raqamni olish
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "order" not in context.user_data:
        return

    phone = update.message.text
    product = context.user_data["order"]
    user = update.message.from_user

    # Admin ga xabar
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🛎 YANGI BUYURTMA!\n\n"
            f"👤 Mijoz: {user.first_name}\n"
            f"🆔 ID: {user.id}\n"
            f"📞 Tel: {phone}\n\n"
            f"📦 Mahsulot: {product['name']}\n"
            f"💰 Narx: {product['price']}"
        )
    )

    await update.message.reply_text(
        "✅ Buyurtmangiz qabul qilindi!\n"
        "Tez orada admin siz bilan bog‘lanadi 🙌"
    )

    context.user_data.clear()

# RUN
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone))

app.run_polling()
