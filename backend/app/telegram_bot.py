from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from .database import get_db
from . import models, auth
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import asyncio
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
application: Optional[Application] = None
task_checker: Optional[asyncio.Task] = None


def get_main_keyboard():
    """Create the main keyboard menu."""
    keyboard = [
        [KeyboardButton(text="🔗 Link Account"),
         KeyboardButton(text="⏱️ Current Activity")],
        [KeyboardButton(text="❓ Help"), KeyboardButton(text="🏠 Start")],
        [KeyboardButton(text="🔓 Unlink Account")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Welcome to PlanTracker Bot!\n\n"
        "Available commands:\n"
        "/link - Link your account\n"
        "/unlink - Unlink your account\n"
        "/current - Show current activity\n"
        "/help - Show help message",
        reply_markup=get_main_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message."""
    await update.message.reply_text(
        "PlanTracker Bot Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/link - Link your account\n"
        "/unlink - Unlink your account\n"
        "/current - Show current activity\n\n"
        "You can use the buttons below to send these commands.",
        reply_markup=get_main_keyboard(),
    )


async def link_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the account linking process."""
    await update.message.reply_text(
        "Please enter your PlanTracker account email:",
        reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),
    )
    context.user_data['state'] = 'waiting_for_email'


async def unlink_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unlink the user's Telegram account."""
    telegram_id = str(update.effective_user.id)
    db = next(get_db())
    try:
        user = db.query(
            models.User).filter(
            models.User.telegram_chat_id == telegram_id).first()
        if not user:
            await update.message.reply_text(
                "Your account is not linked to Telegram.",
                reply_markup=get_main_keyboard(),
            )
            return

        user.telegram_chat_id = None
        db.commit()
        logger.info(f"Successfully unlinked account for user: {user.email}")

        await update.message.reply_text(
            "Your account has been unlinked from Telegram. You will no longer receive notifications.",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error unlinking account: {str(e)}")
        await update.message.reply_text(
            "An error occurred while unlinking your account. Please try again later.",
            reply_markup=get_main_keyboard(),
        )
    finally:
        db.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages based on the current state."""
    message_text = update.message.text
    state = context.user_data.get('state')
    logger.info(f"Handling message: '{message_text}' in state: {state}")

    # Handle button clicks first
    if message_text in ["🔗 Link Account", "⏱️ Current Activity",
                        "❓ Help", "🏠 Start", "🔓 Unlink Account"]:
        await handle_buttons(update, context)
        return

    # If no state is set, ignore the message
    if not state:
        logger.info("No state set, ignoring message")
        return

    if state == 'waiting_for_email':
        email = message_text.strip()
        logger.info(f"Processing email: {email}")
        db = next(get_db())
        try:
            user = db.query(models.User).filter(models.User.email == email).first()
            if not user:
                logger.info(f"User not found for email: {email}")
                await update.message.reply_text(
                    "User not found. Please check your email and try again:",
                    reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),
                )
                return

            if user.telegram_chat_id:
                logger.info(f"Account already linked for email: {email}")
                await update.message.reply_text(
                    "This account is already linked to a Telegram account.\n"
                    "Please unlink it first through the web interface or use the '🔓 Unlink Account' button.",
                    reply_markup=get_main_keyboard(),
                )
                context.user_data.clear()
                return

            context.user_data['email'] = email
            context.user_data['state'] = 'waiting_for_password'
            logger.info(f"Email verified, waiting for password for: {email}")
            await update.message.reply_text(
                "Email verified! Please enter your password:",
                reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),
            )
        except Exception as e:
            logger.error(f"Error in email verification: {str(e)}")
            await update.message.reply_text(
                "An error occurred. Please try again later.",
                reply_markup=get_main_keyboard(),
            )
        finally:
            db.close()

    elif state == 'waiting_for_password':
        password = message_text.strip()
        email = context.user_data.get('email')
        logger.info(f"Processing password for email: {email}")

        if not email:
            logger.error("Email not found in context")
            await update.message.reply_text(
                "An error occurred. Please start the linking process again.",
                reply_markup=get_main_keyboard(),
            )
            context.user_data.clear()
            return

        db = next(get_db())
        try:
            user = auth.authenticate_user(db, email, password)
            if not user:
                logger.info(f"Invalid password for email: {email}")
                await update.message.reply_text(
                    "Invalid password. Please try again:",
                    reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True),
                )
                return

            user.telegram_chat_id = str(update.effective_user.id)
            db.commit()
            logger.info(f"Successfully linked account for email: {email}")

            context.user_data.clear()
            await update.message.reply_text(
                "Account successfully linked! You will now receive notifications about your activities.",
                reply_markup=get_main_keyboard(),
            )
        except Exception as e:
            logger.error(f"Error in password verification: {str(e)}")
            await update.message.reply_text(
                "An error occurred. Please try again later.",
                reply_markup=get_main_keyboard(),
            )
        finally:
            db.close()


async def current_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current activity with timer."""
    telegram_id = str(update.effective_user.id)
    db = next(get_db())
    try:
        user = db.query(
            models.User).filter(
            models.User.telegram_chat_id == telegram_id).first()
        if not user:
            await update.message.reply_text(
                "Please link your account first using the '🔗 Link Account' button.",
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
            await update.message.reply_text(
                "No active timer running.\n"
                "Use the web interface to start tracking an activity.",
                reply_markup=get_main_keyboard(),
            )
            return

        elapsed_time = 0
        if current_activity.last_timer_start:
            # Ensure both datetimes are timezone-aware
            now = datetime.now(timezone.utc)
            last_start = current_activity.last_timer_start.replace(tzinfo=timezone.utc)
            elapsed = now - last_start
            elapsed_time = int(elapsed.total_seconds())

        total_time = current_activity.recorded_time + elapsed_time

        await update.message.reply_text(
            f"Current activity: {current_activity.title}\n"
            f"Time: {format_time(total_time)}\n"
            f"Status: Running",
            reply_markup=get_main_keyboard(),
        )
    except Exception as e:
        logger.error(f"Error getting current activity: {str(e)}")
        await update.message.reply_text(
            "An error occurred while getting current activity.",
            reply_markup=get_main_keyboard(),
        )
    finally:
        db.close()


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    message_text = update.message.text
    logger.info(f"Handling button click: {message_text}")

    if message_text == "🔗 Link Account":
        await link_account(update, context)
    elif message_text == "⏱️ Current Activity":
        await current_activity(update, context)
    elif message_text == "❓ Help":
        await help_command(update, context)
    elif message_text == "🏠 Start":
        await start(update, context)
    elif message_text == "🔓 Unlink Account":
        await unlink_account(update, context)


async def check_upcoming_tasks():
    """Check for tasks that are scheduled to start in 10 minutes and send notifications."""
    while True:
        try:
            db = next(get_db())
            now = datetime.now(timezone.utc)
            ten_minutes_from_now = now + timedelta(minutes=10)

            upcoming_tasks = (
                db.query(models.Activity)
                .filter(
                    models.Activity.scheduled_time >= now,
                    models.Activity.scheduled_time <= ten_minutes_from_now,
                    models.Activity.timer_status == "stopped",
                    models.Activity.notified is False
                )
                .all()
            )

            for task in upcoming_tasks:
                await send_notification(
                    task.user_id,
                    f"Reminder: Task '{task.title}' is scheduled to start in 10 minutes!"
                )
                task.notified = True
                db.commit()

            await asyncio.sleep(60)
        except Exception as e:
            logger.error(f"Error in check_upcoming_tasks: {str(e)}")
            await asyncio.sleep(60)


async def send_notification(user_id: int, message: str):
    """Send a notification to a user."""
    if not application:
        logger.error("Telegram bot not initialized")
        return False

    try:
        db = next(get_db())
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user and user.telegram_chat_id:
            await application.bot.send_message(chat_id=user.telegram_chat_id, text=message)
            return True
        return False
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return False
    finally:
        db.close()


def format_time(seconds):
    """Format seconds into HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


async def start_bot():
    """Start the Telegram bot."""
    global application, task_checker
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
            return

        # Create the application
        application = Application.builder().token(token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("link", link_account))
        application.add_handler(CommandHandler("unlink", unlink_account))
        application.add_handler(CommandHandler("current", current_activity))

        # Add a single message handler for all text messages
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        ))

        # Start the background task for checking upcoming tasks
        task_checker = asyncio.create_task(check_upcoming_tasks())

        # Start the bot without blocking
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        logger.info("Telegram bot started successfully")
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise


async def stop_bot():
    """Stop the Telegram bot."""
    global application, task_checker
    try:
        if task_checker:
            task_checker.cancel()
            try:
                await task_checker
            except asyncio.CancelledError:
                pass
            task_checker = None

        if application:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            application = None
            logger.info("Telegram bot stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping bot: {str(e)}")
        raise
