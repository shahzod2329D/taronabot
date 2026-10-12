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
        "🔗 Ба ман истинод аз YouTube, TikTok, Instagram ё мусиқа фиристед. "
        "Ман видео, аудиои видео ва дар сурати имкон таронаи оригиналиро ба таври худкор меёбам!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    url = message.text.strip()
    if not ("http" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "instagram.com" in url):
        bot.reply_to(message, "⚠️ Лутфан истиноди дуруст фиристед (YouTube, TikTok ё Instagram).")
        return

    msg = bot.reply_to(message, "⏳ Боргирӣ ва ҷустуҷӯи тарона истодааст, лутфан интизор шавед...")

    try:
        api_url = f"https://kaiz-apis.gleeze.com/api/downloader?url={url}"
        response = requests.get(api_url, timeout=30)
        data = response.json()

        video_url = None
        audio_url = None
        song_title = None

        if "data" in data:
            res_data = data["data"]
            video_url = res_data.get("downloadUrl") or res_data.get("url") or res_data.get("video")
            audio_url = res_data.get("audio") or res_data.get("music") or res_data.get("mp3") or res_data.get("dl")
            song_title = res_data.get("title") or res_data.get("song") or res_data.get("music_info")
        elif "result" in data:
            res_data = data["result"]
            video_url = res_data.get("url") or res_data.get("download") or res_data.get("video")
            audio_url = res_data.get("audio") or res_data.get("music") or res_data.get("mp3") or res_data.get("dl")
            song_title = res_data.get("title") or res_data.get("song")

        sent_anything = False

        # 1. Видеоро мефиристем
        if video_url:
            try:
                bot.send_video(message.chat.id, video_url, caption="✅ Видеои шумо!")
                sent_anything = True
            except:
                pass

        # 2. Аудиои кӯтоҳи худи видеоро мефиристем
        if audio_url:
            try:
                bot.send_audio(message.chat.id, audio_url, caption="🎵 Аудиои лаҳзавии видео!")
                sent_anything = True
            except:
                pass
        elif video_url:
            try:
                bot.send_audio(message.chat.id, video_url, caption="🎵 Аудиои ҷудошуда аз видео!")
                sent_anything = True
            except:
                pass

        # 3. Агар номи тарона маълум бошад ё YouTube сурат гирифта бошад, кӯшиш мекунем таронаи пурраро ёбем
        if song_title and isinstance(song_title, str):
            try:
                search_api = f"https://kaiz-apis.gleeze.com/api/yts?search={song_title}"
                search_res = requests.get(search_api, timeout=15).json()
                # Агар натиҷа мавжуд бошад, линки аудиои пурраро мефиристем
                tracks = search_res.get("data") or search_res.get("result")
                if tracks and len(tracks) > 0:
                    full_audio_url = tracks[0].get("url") or tracks[0].get("download")
                    if full_audio_url:
                        bot.send_audio(message.chat.id, full_audio_url, caption=f"🎶 Таронаи оригинал ва пурра: {song_title}")
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
