import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.dispatcher.filters import BaseFilter
from aiogram.exceptions import TelegramBadRequest
from aiogram.types.message import ContentType
from environs import Env

# Logging config
logging.basicConfig(level=logging.INFO)

# Loading .env
env = Env()
env.read_env()

bot_token = env("BOT_TOKEN")
admin_ids = env.list("ADMIN_IDS")
photo_id = env("PHOTO_ID")

tgbot = Bot(token=bot_token, parse_mode="HTML")
dp = Dispatcher()


# Creating a filter that returns True if the user is a chat admin
# and False if it isn't
class IsNotChatAdminFilter(BaseFilter):
    is_not_chat_admin: bool

    async def __call__(self, message: types.Message, bot: Bot) -> bool:
        try:
            chat_admins = await bot.get_chat_administrators(message.chat.id)
            chat_admin_ids = [i.user.id for i in chat_admins]
            return message.from_user.id not in chat_admin_ids
        except TelegramBadRequest as error:
            logging.error(error)


# Binding filter NotAdminFilter
dp.message.bind_filter(IsNotChatAdminFilter)


# Handle service messages like 'new chat member' or 'left chat member'
@dp.message(content_types=[ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER])
async def delete_service_messages(message: types.Message):
    """  Delete service messages  """
    await message.delete()


# Handle links if they weren't sent from admin
@dp.message(F.text.regexp(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"),
    is_not_chat_admin=True
)
async def anti_link(message: types.Message):
    """  Delete any type of links  """
    await message.delete()


@dp.message(F.chat.type == "private", content_types=["photo"])
async def send_update_data(message: types.Message):
    await message.answer(message.photo[-1].file_id)


# Handle command 'start'
@dp.message(F.chat.type == "private", commands=["start"])
async def great(message: types.Message):
    """  Great the user  """
    await message.answer(text="Assalamu Alaykum, {}!".format(message.from_user.full_name))
    await message.answer_photo(
        photo=photo_id,
        caption="Meni o'z guruhingizga qoshing va <u>administrator</u> lavozimini bering va men guruhingizni shu kabi "
                "<code>servis</code> xabarlardan va <code>havolalardan</code> tozalayman.\n"
                "<i>P.S Bizda reklama yo'q :)</i>"
    )


# Handle command 'help'
@dp.message(F.chat.type == "private", commands=["help"])
async def command_help(message: types.Message):
    """  Send help message to user  """
    await message.answer("Har qanday xato, taklif va mulohazalaringizni botni ishlab chiqaruvchisi @AyuB_Ismailoff'ga "
                         "yuboring!\nBizning xizmatlarimizdan foydalanayotganingizdan minnatdormiz)")


# Handle any message in private chat
@dp.message(F.chat.type == "private")
async def any_message(message: types.Message):
    """  Introduce the bot to user  """
    await message.delete()
    await message.answer_photo(
        photo=photo_id,
        caption="Meni o'z guruhingizga qoshing va <u>administrator</u> lavozimini bering va men guruhingizni shu kabi "
                "<code>servis</code> xabarlardan va <code>havolalardan</code> tozalayman.\n"
                "<i>P.S Bizda reklama yo'q :)</i>"
    )


async def on_startup(bot: Bot):
    """  Run commands below when bot starts  """
    # Setting up default commands
    await bot.set_my_commands(commands=[
        types.BotCommand(command="start", description="\U0001F504 Botni qayta yuklash"),
        # Emoji ":arrows_counterclockwise:"
        types.BotCommand(command="help", description="\U0001F198 Yordam")  # Emoji "sos"
    ])

    # Sending message 'Bot started!' to admins
    for admin_id in admin_ids:
        await bot.send_message(admin_id, "Bot started!")


async def on_shutdown(bot: Bot):
    """  Run functions below when bot shuts down  """
    # Deleting my commands
    await bot.delete_my_commands()
    # Sending message 'Bot stopped!' to admins
    for admin_id in admin_ids:
        await bot.send_message(admin_id, "Bot stopped!")


async def main():
    try:
        await on_startup(tgbot)
        await dp.start_polling(tgbot)
    finally:
        await on_shutdown(tgbot)
        await tgbot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
