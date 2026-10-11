import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# Siz bergan ma'lumotlar asosida sozlamalar
API_TOKEN = "Sizning_Bot_Tokeningiz"  # Bot tokeningizni yozasiz
CHANNEL_USERNAME = "@Sizning_Kanal_Linkangiz"  # Majburiy obuna kanalingiz

# Logging sozlamasi
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Kanalga obuna bo'lganligini tekshiruvchi funksiya
async def check_subscription(user_id: int):
    try:
        member = await bot.get_chat_member(
            chat_id=CHANNEL_USERNAME, user_id=user_id
        )
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception:
        return False


# /start buyrug'i (tojik tilida)
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        keyboard = types.InlineKeyboardMarkup()
        join_btn = types.InlineKeyboardButton(
            "Озуна шудан ба канал 📢", url=f"https://t.me/{CHANNEL_USERNAME[1:]}"
        )
        check_btn = types.InlineKeyboardButton(
            "Санҷидан 🔄", callback_data="check_sub"
        )
        keyboard.add(join_btn)
        keyboard.add(check_btn)

        await message.answer(
            "Барои истифодаи бот лутфан аввал ба канали мо обуна шавед:",
            reply_markup=keyboard,
        )
        return

    await message.answer(
        "Салом! Хуш омадед ба Тарона Бот. Суруд ё мусиқии лозимиро фиристед!"
    )


# Obunani tekshirish tugmasi bosilganda
@dp.callback_query_handler(text="check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        await bot.answer_callback_query(
            callback_query.id, text="Ташаккур, обуна тасдиқ шуд! ✅"
        )
        await bot.send_message(
            user_id,
            "Табрик мекунем! Акнун шумо метавонед аз бот пурра истифода баред. Марҳамат, таронаи ҷустуҷӯкардаатонро фиристед.",
        )
    else:
        await bot.answer_callback_query(
            callback_query.id,
            text="Шумо ҳанӯз ба канал обуна нашудаед! ❌",
            show_alert=True,
        )


# Har qanday xabar yoki media kelganda ishlovchi qism
@dp.message_handler(content_types=["text", "audio", "video", "document"])
async def handle_media(message: types.Message):
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)

    if not is_subscribed:
        await message.answer(
            "Лутфан барои истифодаи бот аввал ба канали мо обуна шавед ва фармони /start-ро пахш кунед."
        )
        return

    await message.answer(
        "Дархости шумо қабул шуд! Таронаи шумо ҷустуҷӯ шуда истодааст..."
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
  
