import csv
import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Get token correctly
BOT_TOKEN = os.getenv("7683035959:AAFEQnvsiMGOnS15t6uCHTYC9eMYPrAG1R8")


# Load addresses
def load_address_book(csv_file):
    address_book = {}
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name'].strip().lower()
            lat = float(row['latitude'])
            lon = float(row['longitude'])
            address_book[name] = (lat, lon)
    return address_book


ADDRESS_BOOK = load_address_book("addresses.csv")


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! Send a location name and I’ll show it.\nType /locations to see all places."
    )


# /locations
async def show_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name.title(), callback_data=name)]
        for name in ADDRESS_BOOK.keys()
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("📍 Choose a location:", reply_markup=reply_markup)


# text handler
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower().strip()

    if user_input in ADDRESS_BOOK:
        lat, lon = ADDRESS_BOOK[user_input]
        await update.message.reply_location(latitude=lat, longitude=lon)
    else:
        await update.message.reply_text(
            "❌ Not found. Type /locations to see available places."
        )


# button handler
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    location_name = query.data
    lat, lon = ADDRESS_BOOK[location_name]

    await query.message.reply_location(latitude=lat, longitude=lon)


def main():
    logging.basicConfig(level=logging.INFO)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("locations", show_locations))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    app.add_handler(CallbackQueryHandler(handle_button))

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()