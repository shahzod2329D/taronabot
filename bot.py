import os
import telebot
from telebot import types
from flask import Flask, request
import yt_dlp

TOKEN = "8885376330:AAH-czdsIj-kNyOyAx_iYL39-mOIHh2DAt0"
CHANNEL_USERNAME = "@Kitobhoi_elektroni"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Санҷиши обуна ба канал
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
        "🔗 Ба ман истинод (ссылка) аз YouTube, TikTok ё Instagram фиристед. "
        "Ман видео ё аудиои онро мекашам ва ба шумо мефиристам!"
    )
    bot.reply_to(message, welcome_text)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "Ташаккур, обуна тасдиқ шуд! ✅")
        bot.edit_message_text(
            "🎉 Обунаи шумо бо муваффақият тасдиқ шуд!\n\n"
            "Истиноди видео ё суруди худро фиристед:",
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
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'max_filesize': 50 * 1024 * 1024,
            'noplaylist': True,
        }

        os.makedirs("downloads", exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Агар файл аудио бошад ё формат аудио табдил ёфта бошад
            ext = info.get('ext', '')

        # Фиристодани файл вобаста ба намуди он
        with open(file_path, 'rb') as f:
            if ext in ['mp3', 'm4a', 'wav', 'aac']:
                bot.send_audio(message.chat.id, f, caption="✅ Марҳамат, суруди шумо!")
            else:
                bot.send_video(message.chat.id, f, caption="✅ Марҳамат, видеои шумо!")

        bot.delete_message(message.chat.id, msg.message_id)

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Боргирӣ карда нашуд. Эҳтимол истинод хато аст ё ҳаҷми файл калон аст.",
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🎵 Бот ба кор даромад...")
    
    import threading
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    
    app.run(host="0.0.0.0", port=port)
