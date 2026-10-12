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
        "🎵 Salom! Botimizga xush kelibsiz.\n\n"
        "🔗 Menga YouTube, TikTok, Instagram yoki musiqa havolasini yuboring. "
        "Men uning ham videosini, ham audiosini (musiqasini) avtomatik ravishda topib beraman!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not ("http" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "instagram.com" in url):
        bot.reply_to(message, "⚠️ Iltimos, to'g'ri havola yuboring (YouTube, TikTok yoki Instagram).")
        return

    msg = bot.reply_to(message, "⏳ Qidirilmoqda va yuklab olinmoqda, iltimos kuting...")

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

        # 1. Agar alohida audio/musiqa havolasi topilsa, uni musiqa sifatida yuboramiz
        if audio_url:
            try:
                bot.send_audio(message.chat.id, audio_url, caption="🎵 Topilgan musiqa/audio!")
                sent_anything = True
            except:
                pass

        # 2. Agar video havolasi topilsa, videoni yuboramiz
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption="✅ Marhamat, video!")
                sent_anything = True
                
                # Agar alohida audio topilmagan bo'lsa, lekin video bo'lsa, videoning o'zidan audio yasab yuborishga urinamiz
                if not audio_url:
                    try:
                        bot.send_audio(message.chat.id, video_url, caption="🎵 Videodan ajratilgan audio!")
                    except:
                        pass
            except:
                pass

        if sent_anything:
            bot.delete_message(message.chat.id, msg.message_id)
            return

        bot.edit_message_text(
            "❌ Afsuski, bu havoladan media topib bo'lmadi. Boshqa havola sinab ko'ring.",
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            "❌ Xatolik yuz berdi. Iltimos, birozdan keyin qayta urinib ko'ring.",
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

if __name__ == "__main__":
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("🔗 Webhook muvaffaqiyatli ulandi!")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
