from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor
import redis
import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['exchange'])
async def exchange(message: types.Message):
    args = message.get_args().split()
    if len(args) != 3:
        await message.reply("Usage: /exchange USD RUB 10")
        return
    from_currency, to_currency, amount = args
    amount = float(amount)
    from_rate = float(redis_client.get(from_currency).decode().replace(',', '.'))
    to_rate = float(redis_client.get(to_currency).decode().replace(',', '.'))
    result = (to_rate / from_rate) * amount
    await message.reply(f"{amount} {from_currency} = {result:.2f} {to_currency}")

@dp.message_handler(commands=['rates'])
async def rates(message: types.Message):
    rates = redis_client.keys('*')
    rates_text = "\n".join([f"{key.decode()}: {redis_client.get(key).decode()}" for key in rates])
    await message.reply(f"Current rates:\n{rates_text}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
