from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ReplyKeyboardRemove


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_id: int) -> None:
        self.access_id = access_id
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if int(message.from_user.id) != int(self.access_id):
            await message.answer('В доступе отказано', reply_markup=ReplyKeyboardRemove)
            raise CancelHandler
