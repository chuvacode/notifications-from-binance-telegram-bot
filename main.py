import config
from db import DB
from parser_binance import Parser
import logging
import asyncio

from aiogram import Bot, Dispatcher, executor, types

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# Команда активации подписки
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Вы успешно подписались на рассылку!\nЖдите, скоро выйдут новые обзоры и вы узнаете о них первыми =)")


# Команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if (not db.subscriber_exists(message.from_user.id)):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


parser = Parser()
db = DB()

# Проверка на новые записи и рассклка
async def task():
    if (parser.check_new_article()):
        # получаем список подписчиков бота
        subscriptions = db.get_subscriptions()

        # отправляем всем новость
        for s in subscriptions:
            await bot.send_message(
                s[1],
                text=parser.title+"\n"+"https://www.binance.com/en/support/announcement/" + parser.last_article
            )

DELAY = 5

def repeat(coro, loop):
    asyncio.ensure_future(coro(), loop=loop)
    loop.call_later(DELAY, repeat, coro, loop)

# Запуск
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.call_later(DELAY, repeat, task, loop)
    executor.start_polling(dp, skip_updates=True, loop=loop)
