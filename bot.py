import os
import telebot
from flask import Flask, request
import requests

TOKEN = "8885376330:AAH72wW6JfFdpW3OgU6tQuzPvglb_xhe0a8"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

# Вебхук орқали хабарларни қабул қилиш (409 конфликтни юз фоиз йўқотади)
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎵 Хуш омадед ба боти тарона ва медиа!\n\n"
        "🔗 Ба ман истинод аз YouTube, TikTok ё Instagram фиристед. "
        "Ман видео ва аудиои онро ба таври худкор ба шумо мефиристам!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not ("http" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "instagram.com" in url):
        bot.reply_to(message, "⚠️ Лутфан истиноди дуруст фиристед (YouTube, TikTok ё Instagram).")
        return

    msg = bot.reply_to(message, "⏳ Боргирӣ истодааст, лутфан интизор шавед...")

    try:
        api_url = f"https://apis.davidcyriltech.my.id/download?url={url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()

        if data.get("status") == 200 or "result" in data:
            result = data.get("result", {})
            video_url = result.get("download_url") or result.get("video") or result.get("link")
            audio_url = result.get("audio") or result.get("music")
            
            # Агар видео мавжуд бўлса
            if video_url:
                bot.send_video(message.chat.id, video_url, caption="✅ Видеои шумо!")

            # Агар аудио ёки мусиқа мавжуд бўлса
            if audio_url:
                bot.send_audio(message.chat.id, audio_url, caption="🎵 Аудио/Мусиқаи шумо!")

            if video_url or audio_url:
                bot.delete_message(message.chat.id, msg.message_id)
                return

        bot.edit_message_text(
            "❌ Боргирӣ карда нашуд. Лутфан истиноди дигар санҷед.",
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            "❌ Хатогӣ рух дод. Лутфан баъдтар бори дигар кӯшиш кунед.",
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

if __name__ == "__main__":
    # Render URL орқали вебхукни автоматик улаймиз
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("🔗 Webhook фаъол шуд!")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
