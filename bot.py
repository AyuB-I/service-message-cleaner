import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types.message import ContentType
from environs import Env


# Logging config
logging.basicConfig(level=logging.INFO)

# Loading .env
env = Env()
env.read_env()

bot_token = env("BOT_TOKEN")
admin_ids = env.int("ADMIN_IDS")
photo_id = env("PHOTO_ID")

bot = Bot(token=bot_token, parse_mode="HTML")
dp = Dispatcher()


# Handler to service messages like 'new chat member' or 'left chat member'
@dp.message(content_types=[ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER])
async def delete_service_messages(message: types.Message):
	"""  Delete serice messages  """
	await message.delete()
	logging.info("Deleted message!")

@dp.message(content_types=["photo"])
async def send_update_data(message: types.Message):
	await message.answer(message.photo[-1].file_id)

# Handle any message
@dp.message(commands=["start"])
async def great(message: types.Message):
	"""  Great the user  """
	if message.chat.type == "private":
		await message.answer(text="Assalamu Alaykum, {}!".format(message.from_user.full_name))
		await message.answer_photo(photo=photo_id, 
			caption="<b>Meni o'z guruhingizga qoshing va <i>administrator</i> lavozimini bering " 
			"va men guruhingizni shu kabi habarlardan tozalayman.</b>")


async def on_startup(dp):
	"""  Notify admins when bot started  """
	for admin_id in admin_ids:
		await bot.send_message(admin_id, "Bot started!")

async def main():
	try:
		await dp.start_polling(bot)
		await on_startup()
	finally:
		await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
