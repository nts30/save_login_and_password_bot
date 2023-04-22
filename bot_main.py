from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove
from bot_db import Database
from buttons import choice_kb, cancel_kb, delete_choice_buttons
from middlewares import *

bot = Bot('...')
dp = Dispatcher(bot, storage=MemoryStorage())
admin_id = 735001284
dp.middleware.setup(AccessMiddleware(admin_id))

database = Database('users_bot')


class FSMAdmin(StatesGroup):
    choice = State()
    login = State()
    delete_account = State()
    delete_all_account = State()


def auth(func):
    """Проверка доступа по id

    :param func:
    :return:
    """

    async def wrapper(message, state):
        if message.from_user.id != admin_id:
            return await message.reply('Отказано в доступе', reply_markup=ReplyKeyboardRemove())
        return await func(message, state)

    return wrapper


async def start_message(message: types.Message, state: FSMContext):
    await message.answer('Выберите действие', reply_markup=choice_kb)
    await state.set_state(FSMAdmin.choice.state)


async def choice(message: types.Message, state: FSMContext):
    if message.text.lower() == 'добавить аккаунт':
        await message.answer('Введите логин', reply_markup=cancel_kb)
        await state.set_state(FSMAdmin.login.state)

    elif message.text.lower() == 'удалить аккаунт':
        await message.answer('Введите логин аккаунта, который нужно удалить', reply_markup=cancel_kb)
        await state.set_state(FSMAdmin.delete_account.state)

    elif message.text.lower() == 'удалить все аккаунты':
        await message.answer('Вы действительно хотите удалить все аккаунты?', reply_markup=delete_choice_buttons)
        await state.set_state(FSMAdmin.delete_all_account.state)

    elif message.text.lower() == 'получить информацию':
        all_info = database.read_info()
        for account in all_info:
            await message.answer(account)


async def delete_all_accounts(message: types.Message, state=FSMContext):
    if message.text.lower() == 'да':
        response = database.delete_all_accounts()
        await message.answer(response, reply_markup=choice_kb)
        await state.set_state(FSMAdmin.choice.state)
    elif message.text.lower() == 'нет':
        await message.answer('Действие отменено', reply_markup=choice_kb)
        await state.set_state(FSMAdmin.choice.state)


async def delete_account(message: types.Message, state=FSMContext):
    response = database.delete_account(message.text)
    await message.answer(response)
    await state.set_state(FSMAdmin.choice.state)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_message, commands='start')

    dp.register_message_handler(choice, state=FSMAdmin.choice)

    dp.register_message_handler(delete_all_accounts, state=FSMAdmin.delete_all_account)

    dp.register_message_handler(delete_account, state=FSMAdmin.delete_account)


if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
