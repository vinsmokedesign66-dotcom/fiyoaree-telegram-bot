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

# =========================
# BOT TOKEN
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is missing. Set it in Render environment variables."
    )

# =========================
# LOGGING
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# CSV FILE PATH
# =========================

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "addresses.csv")

# =========================
# LOAD ADDRESS BOOK
# =========================


def load_address_book(csv_file):
    address_book = {}

    try:
        with open(csv_file, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    name = row["name"].strip().lower()
                    lat = float(row["latitude"])
                    lon = float(row["longitude"])

                    address_book[name] = (lat, lon)

                except Exception as e:
                    logging.warning(f"Skipping invalid row: {row} | Error: {e}")

    except FileNotFoundError:
        logging.error("addresses.csv file not found.")
        raise

    return address_book


ADDRESS_BOOK = load_address_book(CSV_PATH)

# =========================
# START COMMAND
# =========================


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello!\n\n"
        "Send a location name and I’ll show you where it is.\n\n"
        "Type /locations to see all available places."
    )

# =========================
# SHOW LOCATIONS
# =========================


async def show_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not ADDRESS_BOOK:
        await update.message.reply_text("❌ No locations available.")
        return

    buttons = []

    for name in ADDRESS_BOOK.keys():
        buttons.append(
            [InlineKeyboardButton(name.title(), callback_data=name)]
        )

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "📍 Choose a location:",
        reply_markup=reply_markup
    )

# =========================
# HANDLE TEXT SEARCH
# =========================


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower().strip()

    if user_input in ADDRESS_BOOK:
        lat, lon = ADDRESS_BOOK[user_input]

        await update.message.reply_location(
            latitude=lat,
            longitude=lon
        )

    else:
        await update.message.reply_text(
            "❌ Location not found.\n"
            "Type /locations to see available places."
        )

# =========================
# HANDLE BUTTON CLICKS
# =========================


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.answer()

    location_name = query.data

    if location_name not in ADDRESS_BOOK:
        await query.message.reply_text("❌ Location not found.")
        return

    lat, lon = ADDRESS_BOOK[location_name]

    await query.message.reply_location(
        latitude=lat,
        longitude=lon
    )

# =========================
# ERROR HANDLER
# =========================


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(
        msg="Exception while handling an update:",
        exc_info=context.error
    )

# =========================
# MAIN FUNCTION
# =========================


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("locations", show_locations))

    # Text messages
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_address
        )
    )

    # Button callbacks
    app.add_handler(CallbackQueryHandler(handle_button))

    # Error logging
    app.add_error_handler(error_handler)

    print("🤖 Bot is running...")

    # Start bot
    app.run_polling()


# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
    main()