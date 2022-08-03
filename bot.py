import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand
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

bot = Bot(token=bot_token, parse_mode="HTML")
dp = Dispatcher()


# Handler to service messages like 'new chat member' or 'left chat member'
@dp.message(content_types=[ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER])
async def delete_service_messages(message: types.Message):
    """  Delete service messages  """
    await message.delete()


@dp.message(content_types=["photo"])
async def send_update_data(message: types.Message):
    await message.answer(message.photo[-1].file_id)


# Handle command 'start'
@dp.message(commadns=["start"])
async def great(message: types.Message):
    """  Great the user  """
    await message.answer(text="Assalamu Alaykum, {}!".format(message.from_user.full_name))
    await message.answer_photo(caption="<b>Meni o'z guruhingizga qoshing va <i>administrator</i> lavozimini bering "
                                       "va men guruhingizni shu kabi habarlardan tozalayman.</b>", photo=photo_id)


# Handle command 'help'
@dp.message(commands=["help"])
async def command_help(message: types.Message):
    """  Send help message to user  """
    await message.answer("Har qanday xato, taklif va mulohazalaringizni botni ishlab chiqaruvchisi @AyuB_Ismailoff'ga "
                         "yuboring!\nBizning xizmatlarimizdan foydalanayotganingizdan minnatdormiz)")


# Handle any message
@dp.message(F.chat.type == "private")
async def any_message(message: types.Message):
    """  Introduce the bot to user  """
    await message.answer_photo(caption="<b>Meni o'z guruhingizga qoshing va <i>administrator</i> lavozimini bering "
                                       "va men guruhingizni shu kabi habarlardan tozalayman.</b>", photo=photo_id)


async def on_startup():
    """  Run commands below when bot starts  """
    # Setting up default commands
    await bot.set_my_commands(commands=[
        types.BotCommand(command="start", description="\U0001F504 Botni qayta yuklash"),  # Emoji ":arrows_counterclockwise:"
        types.BotCommand(command="help", description="\U0001F198 Yordam")  # Emoji "sos"
    ])

    # Sending message 'Bot started!' to admins
    for admin_id in admin_ids:
        await bot.send_message(admin_id, "Bot started!")


async def on_shutdown():
    """  Run functions below when bot shuts down  """
    # Deleting my commands
    await bot.delete_my_commands()
    # Sending message 'Bot stopped!' to admins
    for admin_id in admin_ids:
        await bot.send_message(admin_id, "Bot stopped!")


async def main():
    try:
        await on_startup()
        await dp.start_polling(bot)
    finally:
        await on_shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
