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
        api_url = f"https://kaiz-apis.gleeze.com/api/downloader?url={url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()

        video_url = None
        audio_url = None

        if "data" in data:
            res_data = data["data"]
            video_url = res_data.get("downloadUrl") or res_data.get("url") or res_data.get("video")
            audio_url = res_data.get("audio") or res_data.get("music") or res_data.get("mp3") or res_data.get("dl")
        elif "result" in data:
            res_data = data["result"]
            video_url = res_data.get("url") or res_data.get("download") or res_data.get("video")
            audio_url = res_data.get("audio") or res_data.get("music") or res_data.get("mp3") or res_data.get("dl")

        sent_anything = False

        # 1. Агар алоҳида аудио линки бўлса, уни мефиристем
        if audio_url:
            try:
                bot.send_audio(message.chat.id, audio_url, caption="🎵 Мусиқа/аудиои шумо!")
                sent_anything = True
            except:
                pass

        # 2. Видеоро мефиристем
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption="✅ Видеои шумо!")
                sent_anything = True
                
                # Агар алоҳида аудио бўлмаса, видеонинг ўзидан аудио ясаб юборамиз
                if not audio_url:
                    try:
                        bot.send_audio(message.chat.id, video_url, caption="🎵 Аудио аз видео!")
                    except:
                        pass
            except:
                pass

        if sent_anything:
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
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("🔗 Webhook фаъол шуд!")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
