import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Созламалар
API_TOKEN = "8885376330:AAH-czdsIj-kNy0yAx_iYL39-mOIHh2DAt0"
CHANNEL_USERNAME = "@taronabot_kanal"

# Logging созламаси
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Мажбурий обунани текшириш функцияси
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Обунани текширишда хатолик: {e}")
        return False

# /start буйруғи
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        keyboard = types.InlineKeyboardMarkup()
        channel_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
        keyboard.add(types.InlineKeyboardButton(text="📢 Kanalga obuna bo'lish", url=channel_link))
        keyboard.add(types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub"))
        
        await message.reply(
            "Ботдан фойдаланиш учун аввал қуйидаги каналимизга обуна бўлинг:",
            reply_markup=keyboard
        )
        return

    await message.reply("Ассалому алайкум! Tarona Bot'га хуш келибсиз. Керакли қўшиқ ёки таронани топиш учун номини ёзиб юборинг.")

# Обунани текшириш тугмаси босилганда
@dp.callback_query_handler(text="check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        await bot.answer_callback_query(callback_query.id, text="Раҳмат, обуна тасдиқланди! ✅")
        await bot.send_message(user_id, "Энди ботдан бемалол фойдаланишингиз мумкин!")
    else:
        await bot.answer_callback_query(callback_query.id, text="Сиз ҳали каналга обуна бўлмапсиз! ❌", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    
