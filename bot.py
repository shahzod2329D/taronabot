import os
import telebot
from flask import Flask, request
import requests

TOKEN = "8885376330:AAH72wW6JfFdpW3OgU6tQuzPvglb_xhe0a8"
CHANNEL_USERNAME = "@Kitobhoi_elektroni"

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

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
    except:
        pass
    return False

def get_subscription_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("📢 Обуна шудан", url="https://t.me/Kitobhoi_elektroni")
    btn_check = telebot.types.InlineKeyboardButton("🔄 Санҷиши обуна", callback_data="check_sub")
    markup.add(btn)
    markup.add(btn_check)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not check_subscription(user_id):
        bot.reply_to(
            message, 
            f"❌ Барои истифодаи бот, лутфан аввал ба канали мо обуна шавед:\n{CHANNEL_USERNAME}", 
            reply_markup=get_subscription_markup()
        )
        return

    welcome_text = (
        "🎵 Хуш омадед!\n\n"
        "🔗 Истиноди YouTube, TikTok ё Instagram фиристед. "
        "Ман видео ва аудиои онро ба таври худкор мефиристам!"
    )
    bot.reply_to(message, welcome_text)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if check_subscription(user_id):
        bot.answer_callback_query(call.id, "✅ Ташаккур, шумо ба канал обуна шудед!")
        bot.send_message(call.message.chat.id, "🎉 Акнун метавонед истиноди худро фиристед!")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
    else:
        bot.answer_callback_query(call.id, "❌ Шумо ҳанӯз ба канал обуна нашудаед!", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    user_id = message.from_user.id

    if not check_subscription(user_id):
        bot.reply_to(
            message, 
            f"❌ Барои гирифтани медиа, лутфан аввал ба канали мо обуна шавед:\n{CHANNEL_USERNAME}", 
            reply_markup=get_subscription_markup()
        )
        return

    url = message.text.strip()
    if not ("http" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "instagram.com" in url):
        bot.reply_to(message, "⚠️ Лутфан истиноди дуруст фиристед (YouTube, TikTok ё Instagram).")
        return

    msg = bot.reply_to(message, "⏳ Боргирӣ истодааст...")

    video_url = None
    audio_url = None

    try:
        # 1-умин усули API (Cobalt ё шубҳасиз ишончли манба)
        api_url = f"https://co.wuk.sh/api/json"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        body = {"url": url, "vQuality": "720"}
        res = requests.post(api_url, json=body, headers=headers, timeout=20)
        res_data = res.json()
        
        if res_data.get("status") == "stream" or res_data.get("status") == "redirect":
            video_url = res_data.get("url")
        elif res_data.get("status") == "picker":
            picker_items = res_data.get("picker", [])
            if picker_items:
                video_url = picker_items[0].get("url")
    except Exception as e:
        print(f"Cobalt API xatosi: {e}")

    # Агар биринчи API орқали топилмаса, захира API'ни ишлатамиз
    if not video_url:
        try:
            backup_url = f"https://kaiz-apis.gleeze.com/api/downloader?url={url}"
            response = requests.get(backup_url, timeout=20).json()
            if "data" in response and isinstance(response["data"], dict):
                r = response["data"]
                video_url = r.get("downloadUrl") or r.get("url") or r.get("video")
                audio_url = r.get("audio") or r.get("music") or r.get("mp3")
            elif "result" in response and isinstance(response["result"], dict):
                r = response["result"]
                video_url = r.get("url") or r.get("download") or r.get("video")
                audio_url = r.get("audio") or r.get("music")
        except Exception as e:
            print(f"Backup API xatosi: {e}")

    sent_anything = False

    try:
        if audio_url:
            bot.send_audio(message.chat.id, audio_url, caption="🎵 Мусиқаи шумо!")
            sent_anything = True
    except:
        pass

    try:
        if video_url:
            bot.send_video(message.chat.id, video_url, caption="✅ Видеои шумо!")
            sent_anything = True
            
            if not audio_url:
                try:
                    bot.send_audio(message.chat.id, video_url, caption="🎵 Аудио аз видео!")
                except:
                    pass
    except:
        pass

    try:
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        pass

    if not sent_anything:
        bot.reply_to(message, "❌ Мутаассифона, ин истинод бор карда нашуд ё сервер банд аст.")

if __name__ == "__main__":
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("🔗 Webhook фаъол шуд!")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
