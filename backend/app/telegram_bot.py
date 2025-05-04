import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session
from datetime import datetime
import os
from . import models, database, auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_confirmation_code = State()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

verification_codes = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Hello there! I am a PlanTracker bot.\n"
        "To connect an account with Telegram, use the command /link\n"
        "Available commands:\n"
        "/help - help\n"
        "/link - link account\n"
        "/current - current activity"
    )

@dp.message(Command("link"))
async def cmd_link(message: types.Message, state: FSMContext):
    await state.set_state(LinkStates.waiting_for_email)
    await message.answer("Enter the email address of your PlanTracker account:")

@dp.message(LinkStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    
    db = next(database.get_db())
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        await message.answer("The user with this email was not found. Try again:")
        return
    
    import random
    code = str(random.randint(100000, 999999))
    verification_codes[email] = {
        'code': code,
        'telegram_id': message.from_user.id,
        'expires': datetime.now().timestamp() + 600  # 10 минут
    }
    
    # Send code to email (using fastapi-mail)
    # TODO: integrate
    
    await state.update_data(email=email)
    await state.set_state(LinkStates.waiting_for_confirmation_code)
    await message.answer(
        f"The confirmation code has been sent to {email}\n"
        "Enter the code from the email:"
    )


@dp.message(LinkStates.waiting_for_confirmation_code)
async def process_confirmation_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    email = data.get('email')
    
    # if email not in verification_codes:
    #     await message.answer("The code has expired. Start over with /link")
    #     await state.clear()
    #     return
    
    # verification_data = verification_codes[email]
    
    # if verification_data['code'] != code:
    #     await message.answer("Invalid code. Try again:")
    #     return
    
    # if datetime.now().timestamp() > verification_data['expires']:
    #     await message.answer("The code has expired. Start over with /link")
    #     del verification_codes[email]
    #     await state.clear()
    #     return
    
    db = next(database.get_db())
    user = db.query(models.User).filter(models.User.email == email).first()
    user.telegram_chat_id = str(message.from_user.id)
    db.commit()
    
    del verification_codes[email]
    await state.clear()
    await message.answer("The account has been successfully linked! You will now receive notifications.")


@dp.message(Command("current"))
async def cmd_current(message: types.Message):
    telegram_id = str(message.from_user.id)
    db = next(database.get_db())
    
    user = db.query(models.User).filter(models.User.telegram_chat_id == telegram_id).first()
    if not user:
        await message.answer("First, link the account with the /link command")
        return
    
    current_activity = db.query(models.Activity).filter(
        models.Activity.user_id == user.id,
        models.Activity.timer_status == "running"
    ).first()
    
    if not current_activity:
        await message.answer("There are no active tasks with the timer running")
        return
    
    elapsed_time = 0
    if current_activity.last_timer_start:
        elapsed = datetime.now() - current_activity.last_timer_start
        elapsed_time = int(elapsed.total_seconds())
    
    total_time = current_activity.recorded_time + elapsed_time
    
    await message.answer(
        f"Current activity: {current_activity.title}\n"
        f"Time: {format_time(total_time)}\n"
        f"Timer status: ▶️ Running"
    )

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


async def send_notification(user_id: int, message: str):
    db = next(database.get_db())
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user and user.telegram_chat_id:
        try:
            await bot.send_message(user.telegram_chat_id, message)
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")

async def start_bot():
    logger.info("Starting telegram bot...")
    await dp.start_polling(bot)

async def stop_bot():
    logger.info("Stopping telegram bot...")
    await dp.stop_polling()
    await bot.session.close()