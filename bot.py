import os
import telebot
from telebot import types
from flask import Flask, request
import requests

TOKEN = "8885376330:AAH72wW6JfFdpW3OgU6tQuzPvglb_xhe0a8"
CHANNEL_USERNAME = "@Kitobhoi_elektroni"

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly!"

# Вебхук орқали Telegram'дан келаётган хабарларни қабул қилиш
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
    except:
        pass
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton("📢 Обуна шудан ба канал", url="https://t.me/Kitobhoi_elektroni")
        btn_check = types.InlineKeyboardButton("🔄 Санҷиши обуна", callback_data="check_sub")
        markup.add(btn_channel)
        markup.add(btn_check)

        bot.reply_to(
            message,
            "⚠️ Барои истифода аз бот, лутфан аввал ба канали мо обуна шавед!\n\n"
            "Пас аз обуна шудан, тугмаи «Санҷиши обуна»-ро пахш кунед.",
            reply_markup=markup
        )
        return

    welcome_text = (
        "🎵 Хуш омадед ба боти тарона ва медиа!\n\n"
        "🔗 Ба ман истинод аз YouTube, TikTok ё Instagram фиристед. "
        "Ман видеои онро мекашам ва ба шумо мефиристам!"
    )
    bot.reply_to(message, welcome_text)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "Ташаккур, обуна тасдиқ шуд! ✅")
        bot.edit_message_text(
            "🎉 Обунаи шумо бо муваффақият тасдиқ шуд!\n\n"
            "Истиноди видеои худро фиристед:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    else:
        bot.answer_callback_query(call.id, "Шумо ҳанӯз ба канал обуна нашудаед! ❌", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        send_welcome(message)
        return

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
            
            if video_url:
                bot.send_video(message.chat.id, video_url, caption="✅ Марҳамат, видеои шумо!")
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
            chat.id=message.chat.id,
            message_id=msg.message_id
        )

if __name__ == "__main__":
    # Вебхукни автоматик улаш учун render URL'ни оламиз
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_URL}/{TOKEN}")
        print("🔗 Webhook бо муваффақият фаъол шуд!")

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
