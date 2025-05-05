import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import os
import asyncio
from . import models, database, auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Create keyboard menu


def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="🔗 Link Account"),
                types.KeyboardButton(text="⏱️ Current Activity"),
            ],
            [
                types.KeyboardButton(text="❓ Help"),
                types.KeyboardButton(text="🏠 Start"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Hello there! I am a PlanTracker bot.\n"
        "To connect an account with Telegram, use the command /link\n"
        "Available commands:\n"
        "/help - help\n"
        "/link - link account\n"
        "/current - current activity",
        reply_markup=get_main_keyboard(),
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "PlanTracker Bot Commands:\n\n"
        "/start - Start the bot and see available commands\n"
        "/help - Show this help message\n"
        "/link - Link your PlanTracker account with Telegram\n"
        "/current - Show your current activity with timer\n"
        "\n"
        "To link your account:\n"
        "1. Use /link command\n"
        "2. Enter your email\n"
        "3. Enter your password\n"
        "\n"
        "After linking, you'll receive notifications about your activities.",
        reply_markup=get_main_keyboard(),
    )


@dp.message(Command("link"))
async def cmd_link(message: types.Message, state: FSMContext):
    await state.set_state(LinkStates.waiting_for_email)
    await message.answer(
        "Enter the email address of your PlanTracker account:",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(LinkStates.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text.strip()

    db = next(database.get_db())
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        await message.answer(
            "The user with this email was not found. Try again:",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    await state.update_data(email=email)
    await state.set_state(LinkStates.waiting_for_password)
    await message.answer(
        "Enter your password:", reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message(LinkStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    data = await state.get_data()
    email = data.get("email")

    db = next(database.get_db())
    user = auth.authenticate_user(db, email, password)

    if not user:
        await message.answer(
            "Invalid password. Try again:", reply_markup=types.ReplyKeyboardRemove()
        )
        return

    user.telegram_chat_id = str(message.from_user.id)
    db.commit()

    await state.clear()
    await message.answer(
        "The account has been successfully linked! You will now receive notifications.",
        reply_markup=get_main_keyboard(),
    )


@dp.message(Command("current"))
async def cmd_current(message: types.Message):
    telegram_id = str(message.from_user.id)
    db = next(database.get_db())

    user = (
        db.query(models.User)
        .filter(models.User.telegram_chat_id == telegram_id)
        .first()
    )
    if not user:
        await message.answer(
            "First, link the account with the /link command",
            reply_markup=get_main_keyboard(),
        )
        return

    current_activity = (
        db.query(models.Activity)
        .filter(
            models.Activity.user_id == user.id,
            models.Activity.timer_status == "running",
        )
        .first()
    )

    if not current_activity:
        await message.answer(
            "There are no active tasks with the timer running",
            reply_markup=get_main_keyboard(),
        )
        return

    elapsed_time = 0
    if current_activity.last_timer_start:
        elapsed = datetime.utcnow() - current_activity.last_timer_start
        elapsed_time = int(elapsed.total_seconds())

    total_time = current_activity.recorded_time + elapsed_time

    await message.answer(
        f"Current activity: {current_activity.title}\n"
        f"Time: {format_time(total_time)}\n"
        f"Timer status: ▶️ Running",
        reply_markup=get_main_keyboard(),
    )


# Handle button clicks


@dp.message(
    lambda message: message.text
    in ["🔗 Link Account", "⏱️ Current Activity", "❓ Help", "🏠 Start"]
)
async def handle_buttons(message: types.Message, state: FSMContext):
    if message.text == "🔗 Link Account":
        await cmd_link(message, state)
    elif message.text == "⏱️ Current Activity":
        await cmd_current(message)
    elif message.text == "❓ Help":
        await cmd_help(message)
    elif message.text == "🏠 Start":
        await cmd_start(message, state)


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


async def check_upcoming_tasks():
    """Check for tasks that are scheduled to start in 10 minutes and send notifications."""
    while True:
        try:
            db = next(database.get_db())
            now = datetime.utcnow()
            ten_minutes_from_now = now + timedelta(minutes=10)
            logger.info(f"[NOTIFY] Now: {now.isoformat()}, 10min from now: {ten_minutes_from_now.isoformat()}")

            # Find tasks scheduled to start in the next 10 minutes
            upcoming_tasks = (
                db.query(models.Activity)
                .filter(
                    models.Activity.scheduled_time >= now,
                    models.Activity.scheduled_time <= ten_minutes_from_now,
                    models.Activity.timer_status == "stopped",
                    models.Activity.notified == False
                )
                .all()
            )
            logger.info(f"[NOTIFY] Found {len(upcoming_tasks)} upcoming tasks")

            for task in upcoming_tasks:
                logger.info(f"[NOTIFY] Task id={task.id}, title='{task.title}', scheduled_time={task.scheduled_time}, timer_status={task.timer_status}")
                await send_notification(
                    task.user_id,
                    f"🔔 Reminder: Task '{task.title}' is scheduled to start in 10 minutes!"
                )
                task.notified = True  # Mark that we've sent the notification
                db.commit()

            # Sleep for 1 minute before checking again
            await asyncio.sleep(60)

        except Exception as e:
            logger.error(f"Error in check_upcoming_tasks: {e}")
            await asyncio.sleep(60)  # Sleep for 1 minute before retrying


async def start_bot():
    logger.info("Starting telegram bot...")
    # Start the background task for checking upcoming tasks
    asyncio.create_task(check_upcoming_tasks())
    await dp.start_polling(bot)


async def stop_bot():
    logger.info("Stopping telegram bot...")
    await dp.stop_polling()
    await bot.session.close()
