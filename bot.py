import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import exceptions, executor
from dotenv import load_dotenv

from main import get_salary_aggregation
from validator import data_validator

load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
MAX_LENGTH_MESSAGE = 4096

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply(f'Привет, {message.from_user.username}')


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply('Пример входных данных:'
                        '{"dt_from": "2022-10-01T00:00:00", '
                        '"dt_upto": "2022-11-30T23:59:00",'
                        '"group_type": "day"}')


@dp.message_handler()
async def get_salary(message: types.Message):
    data = data_validator(message.text)
    error = data.get('error')
    if error:
        await message.reply(error)
    else:
        text = await get_salary_aggregation(data.get('data'))
        text = str(text).replace("'", '"')
        try:
            await message.answer(text)
        except exceptions.MessageIsTooLong:
            await message.answer('Слишком большая выборка')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
