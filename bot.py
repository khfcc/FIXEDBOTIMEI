import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim IMEI (15 digit) dan saya akan cari infonya dari IMEI24.")

def is_valid_imei(imei: str) -> bool:
    return imei.isdigit() and len(imei) == 15

def fetch_imei_info(imei: str) -> str:
    url = f"https://www.imei24.com/check/imei/{imei}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("h1").text.strip()
        info_div = soup.find("div", class_="imei-info")

        if not info_div:
            return "❌ Tidak ditemukan informasi IMEI pada IMEI24."

        rows = info_div.find_all("div", class_="row")
        result_lines = [title]

        for row in rows:
            label = row.find("div", class_="col-xs-5").text.strip()
            value = row.find("div", class_="col-xs-7").text.strip()
            result_lines.append(f"{label}: {value}")

        return "\n".join(result_lines)

    except Exception as e:
        print("❌ Error saat mengambil data IMEI24:", e)
        return "❌ Gagal mengambil data dari IMEI24."

async def handle_imei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = update.message.text.strip()

    if not is_valid_imei(imei):
        await update.message.reply_text("❌ IMEI tidak valid. Harus 15 digit angka.")
        return

    await update.message.reply_text("🔍 Memeriksa IMEI di IMEI24...")
    result = fetch_imei_info(imei)
    await update.message.reply_text(result)

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN tidak ditemukan.")
        exit(1)

    print("🤖 Bot berjalan dengan IMEI24...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_imei))
    app.run_polling()
