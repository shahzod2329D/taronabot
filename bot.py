import os
import telebot
from telebot import types

TOKEN = "8615719131:AAG1nVSZDIG1YTj7nkzmUMQKlinra93DWfg"
CHANNEL_USERNAME = "@Kitobhoi_elektroni"

bot = telebot.TeleBot(TOKEN)

# Каналга обуна бўлганини текшириш функцияси
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
        "🔗 Ба ман линки видео аз YouTube, TikTok ё Instagram фиристед. "
        "Ман видео ва аудиои онро ба шумо меёбам ва мефиристам!"
    )
    bot.reply_to(message, welcome_text)

@bot.callback_query_handler(func=lambda call: call.data == "check_sub")
def callback_check(call):
    user_id = call.from_user.id
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "Ташаккур, обуна тасдиқ шуд! ✅")
        bot.edit_message_text(
            "🎉 Обунаи шумо бо муваффақият тасдиқ шуд!\n\n"
            "Линки видеои худро аз YouTube, TikTok ё Instagram фиристед:",
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

    url = message.text
    if "http" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url or "instagram.com" in url:
        bot.reply_to(message, f"✅ Линки қабул шуд:\n`{url}`\n\n🎬 Видео ва 🎵 аудио тайёр шуда истодааст...", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Лутфан линки дурусти видеоро фиристед (масалан, линки YouTube, TikTok ё Instagram).")

if __name__ == "__main__":
    print("🎵 Бот бо YouTube ва забони тожикӣ ба кор даромад...")
    bot.infinity_polling()
