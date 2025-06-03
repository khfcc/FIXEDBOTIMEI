import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
IMEIDB_API_TOKEN = os.getenv("IMEIDB_API_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim IMEI (15 digit) dan saya akan cari infonya.")

def is_valid_imei(imei: str) -> bool:
    return imei.isdigit() and len(imei) == 15

async def handle_imei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    imei = update.message.text.strip()

    if not is_valid_imei(imei):
        await update.message.reply_text("❌ IMEI tidak valid. Harus 15 digit angka.")
        return

    url = f"https://api.imeidb.xyz/imei/{imei}"
    headers = {"Authorization": f"Bearer {IMEIDB_API_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            await update.message.reply_text("❌ Respons bukan JSON valid.")
            print("Invalid JSON response:", response.text)
            return

        print("✅ API Response:", data)

        brand = data.get("brand")
        model = data.get("model")

        if brand and model:
            reply = f"📱 IMEI Info:\nBrand: {brand}\nModel: {model}"
        else:
            reply = "⚠️ Data tidak lengkap. Respons API:\n" + str(data)

        await update.message.reply_text(reply)

    except requests.exceptions.HTTPError as e:
        await update.message.reply_text(f"❌ HTTP Error: {response.status_code}")
        print("HTTP error:", e)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("❌ Gagal menghubungi API.")
        print("Request error:", e)
    except Exception as e:
        await update.message.reply_text(f"❌ Terjadi kesalahan internal: {str(e)}")
        print("Unexpected error:", e)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_imei))
    print("🤖 Bot berjalan...")
    app.run_polling()
