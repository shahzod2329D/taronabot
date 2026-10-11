import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Танзимотҳо (Созламалар)
API_TOKEN = "8885376330:AAH-czdsIj-kNy0yAx_iYL39-mOIHh2DAt0"
CHANNEL_USERNAME = "@Kitobhoi_elektroni"

# Танзими логинг
logging.basicConfig(level=logging.INFO)

# Эҷоди Bot ва Dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Функцияи санҷиши обунаи ҳатмӣ ба канал
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
        return False
    except Exception as e:
        logging.error(f"Хатогӣ дар санҷиши обуна: {e}")
        return False

# Фармони /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if not is_subscribed:
        keyboard = types.InlineKeyboardMarkup()
        channel_link = f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}"
        keyboard.add(types.InlineKeyboardButton(text="📢 обуна шудан ба канал", url=channel_link))
        keyboard.add(types.InlineKeyboardButton(text="✅ Санҷиши обуна", callback_data="check_sub"))
        
        await message.reply(
            "Барои истифодаи бот лутфан аввал ба канали зерин обуна шавед:",
            reply_markup=keyboard
        )
        return

    await message.reply("Ассалому алайкум! Хуш омадед ба Tarona Bot. Барои ёфтани суруд ё тарона номи онро нависед.")

# Тугмаи санҷиши обуна
@dp.callback_query_handler(text="check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        await bot.answer_callback_query(callback_query.id, text="Ташаккур, обуна тасдиқ шуд! ✅")
        await bot.send_message(user_id, "Акнун шумо метавонед бемалол аз бот истифода баред!")
    else:
        await bot.answer_callback_query(callback_query.id, text="Шумо ҳанӯз ба канал обуна нашудаед! ❌", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
