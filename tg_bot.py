import logging
import random
import uuid

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import Telegram
from tools import save_to_csv, load_samples, user_buffers, model, update_user_stats, pending_texts

logging.basicConfig(level=logging.INFO)
bot = Bot(token=Telegram.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()


@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id == Telegram.admin_id:
        await message.answer("Вы администратор. Для вас действует отдельный режим модерации.")
        return

    samples = load_samples()
    random.shuffle(samples)
    buf = []
    for text in samples:
        sid = uuid.uuid4().hex
        pending_texts[sid] = text
        buf.append(sid)
    user_buffers[user_id] = buf
    await message.answer("Добро пожаловать! Оценивайте сообщения как буллинг или нет.")
    await send_next_sample(user_id)


async def send_next_sample(user_id: int):
    buf = user_buffers.get(user_id, [])
    if not buf:
        await bot.send_message(user_id, "Все размечено, спасибо за помощь!")
        return

    sid = buf.pop()
    text = pending_texts[sid]
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text='✅ Буллинг', callback_data=f'user|{sid}|1'),
        InlineKeyboardButton(text='❌ Не буллинг', callback_data=f'user|{sid}|0')
    )
    await bot.send_message(user_id, f"<b>Оцените сообщение:</b>\n<pre>{text}</pre>", reply_markup=keyboard.as_markup())


@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    try:
        parts = callback.data.split('|')
        mode = parts[0]
        sid = parts[1]
        label_int = int(parts[2])
        text = pending_texts.get(sid)
        if not text:
            await callback.answer("Сессия устарела, перезапустите /start", show_alert=True)
            return

        save_to_csv(text, label_int)
        if mode == 'user':
            update_user_stats(callback.from_user.id)
        # Обновляем сообщение
        await callback.message.edit_text(
            f"<pre>{text}</pre>\n\n<b>Отмечено как:</b> {'Буллинг' if label_int == 1 else 'Не буллинг'}",
            reply_markup=None
        )
        await callback.answer("Ответ сохранен")
        if mode == 'user':
            await send_next_sample(callback.from_user.id)
    except Exception as e:
        logging.exception(f"Ошибка обработки callback: {e}")
        await callback.answer("Произошла ошибка")


@dp.message(F.chat.type.in_(['group', 'supergroup']))
async def handle_message(message: types.Message):
    if not message.text:
        return

    pred = model.predict([message.text])[0]
    if pred == 1:
        try:
            await message.delete()
            sid = uuid.uuid4().hex
            pending_texts[sid] = message.text
            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(text='✅ Буллинг', callback_data=f'admin|{sid}|1'),
                InlineKeyboardButton(text='❌ Не буллинг', callback_data=f'admin|{sid}|0')
            )
            await bot.send_message(
                ADMIN_ID,
                f"<b>Удалено сообщение:</b>\n<pre>{message.text}</pre>",
                reply_markup=keyboard.as_markup()
            )
        except Exception as e:
            logging.exception(f"Ошибка удаления/отправки: {e}")


# Register router
dp.include_router(router)
