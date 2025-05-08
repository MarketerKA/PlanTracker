from app.telegram_bot import format_time
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.telegram_bot import (
    start, help_command, link_account, handle_message, current_activity,
    handle_buttons, check_upcoming_tasks, send_notification, start_bot, stop_bot
)
from app.models import User, Activity
import os
from datetime import datetime, timedelta, timezone
from telegram import Update, Message, Chat, User as TelegramUser
from telegram.ext import ContextTypes
import asyncio


def test_format_time():
    assert format_time(0) == "00:00:00"
    assert format_time(59) == "00:00:59"
    assert format_time(60) == "00:01:00"
    assert format_time(3661) == "01:01:01"

# Mock data
MOCK_TELEGRAM_USER = TelegramUser(
    id=123456789,
    is_bot=False,
    first_name="Test",
    last_name="User",
    username="testuser"
)

MOCK_CHAT = Chat(
    id=123456789,
    type="private"
)

MOCK_MESSAGE = Message(
    message_id=1,
    date=datetime.now(timezone.utc),
    chat=MOCK_CHAT,
    from_user=MOCK_TELEGRAM_USER
)

@pytest.fixture
def mock_message():
    """Create a mock Message object."""
    message = AsyncMock(spec=Message)
    message.chat = MOCK_CHAT
    message.from_user = MOCK_TELEGRAM_USER
    message.text = ""
    return message

@pytest.fixture
def mock_update(mock_message):
    """Create a mock Update object."""
    update = AsyncMock(spec=Update)
    update.effective_user = MOCK_TELEGRAM_USER
    update.message = mock_message
    return update

@pytest.fixture
def mock_context():
    """Create a mock Context object."""
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    with patch('app.telegram_bot.get_db') as mock_get_db:
        mock_session = MagicMock()
        mock_get_db.return_value = iter([mock_session])
        yield mock_session

@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """Test the /start command."""
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Welcome to PlanTracker Bot" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_help_command(mock_update, mock_context):
    """Test the /help command."""
    await help_command(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "PlanTracker Bot Commands" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_link_account_command(mock_update, mock_context):
    """Test the /link command."""
    await link_account(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Please enter your PlanTracker account email" in mock_update.message.reply_text.call_args[0][0]
    assert mock_context.user_data['state'] == 'waiting_for_email'

@pytest.mark.asyncio
async def test_handle_message_email_not_found(mock_update, mock_context, mock_db):
    """Test handling email input when user is not found."""
    mock_context.user_data['state'] = 'waiting_for_email'
    mock_update.message.text = "nonexistent@example.com"
    mock_db.query.return_value.filter.return_value.first.return_value = None

    await handle_message(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "User not found" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_message_email_success(mock_update, mock_context, mock_db):
    """Test handling email input when user is found."""
    mock_context.user_data['state'] = 'waiting_for_email'
    mock_update.message.text = "test@example.com"
    
    mock_user = MagicMock(spec=User)
    mock_user.telegram_chat_id = None
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    await handle_message(mock_update, mock_context)
    assert mock_context.user_data['state'] == 'waiting_for_password'
    assert mock_context.user_data['email'] == "test@example.com"
    mock_update.message.reply_text.assert_called_once()
    assert "Email verified" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_message_password_success(mock_update, mock_context, mock_db):
    """Test handling password input with successful authentication."""
    mock_context.user_data['state'] = 'waiting_for_password'
    mock_context.user_data['email'] = "test@example.com"
    mock_update.message.text = "correct_password"
    
    mock_user = MagicMock(spec=User)
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch('app.telegram_bot.auth.authenticate_user', return_value=mock_user):
        await handle_message(mock_update, mock_context)
        
        assert mock_user.telegram_chat_id == str(MOCK_TELEGRAM_USER.id)
        mock_db.commit.assert_called_once()
        mock_update.message.reply_text.assert_called_once()
        assert "Account successfully linked" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_message_password_invalid(mock_update, mock_context, mock_db):
    """Test handling password input with invalid password."""
    mock_context.user_data['state'] = 'waiting_for_password'
    mock_context.user_data['email'] = "test@example.com"
    mock_update.message.text = "wrong_password"
    
    with patch('app.telegram_bot.auth.authenticate_user', return_value=None):
        await handle_message(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        assert "Invalid password" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_current_activity_no_user(mock_update, mock_context, mock_db):
    """Test current activity when user is not linked."""
    mock_db.query.return_value.filter.return_value.first.return_value = None

    await current_activity(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "Please link your account first" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_current_activity_no_activity(mock_update, mock_context, mock_db):
    """Test current activity when no activity is running."""
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_db.query.return_value.filter.return_value.first.side_effect = [mock_user, None]

    await current_activity(mock_update, mock_context)
    
    mock_update.message.reply_text.assert_called_once()
    assert "No active timer running" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_buttons(mock_update, mock_context):
    """Test handling button clicks."""
    # Test Link Account button
    mock_update.message.text = "🔗 Link Account"
    await handle_buttons(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "Please enter your PlanTracker account email" in mock_update.message.reply_text.call_args[0][0]

    # Reset mock
    mock_update.message.reply_text.reset_mock()
    
    # Test Help button
    mock_update.message.text = "❓ Help"
    await handle_buttons(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()
    assert "PlanTracker Bot Commands" in mock_update.message.reply_text.call_args[0][0]

@pytest.mark.asyncio
async def test_check_upcoming_tasks(mock_db):
    """Test checking upcoming tasks."""
    # Mock the current time
    now = datetime.now(timezone.utc)
    mock_activity = MagicMock(spec=Activity)
    mock_activity.title = "Test Task"
    mock_activity.scheduled_time = now + timedelta(minutes=5)
    mock_activity.timer_status = "stopped"
    mock_activity.notified = False
    mock_activity.user_id = 1

    # Mock the database query to return our test activity
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]

    # Mock the send_notification function
    with patch('app.telegram_bot.send_notification', new_callable=AsyncMock) as mock_send:
        # Create a task that will run check_upcoming_tasks once
        task = asyncio.create_task(check_upcoming_tasks())
        
        # Wait a short time for the task to process
        await asyncio.sleep(0.1)
        
        # Cancel the task to prevent infinite loop
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify the notification was sent
        mock_send.assert_called_once_with(
            mock_activity.user_id,
            f"Reminder: Task '{mock_activity.title}' is scheduled to start in 10 minutes!"
        )
        
        # Verify the activity was marked as notified
        assert mock_activity.notified
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_send_notification_no_user(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with patch('app.telegram_bot.get_db', return_value=iter([mock_db])):
        result = await send_notification(1, "Test message")
        assert result is False

@pytest.mark.asyncio
async def test_send_notification_success(mock_db):
    """Test sending notification successfully."""
    mock_user = MagicMock(spec=User)
    mock_user.email = 'test@example.com'
    mock_user.telegram_chat_id = '123456'
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    mock_application = AsyncMock()
    with patch('app.telegram_bot.application', mock_application), \
         patch('app.telegram_bot.get_db', return_value=iter([mock_db])):
        result = await send_notification(1, "Test message")
        assert result is True
        mock_application.bot.send_message.assert_called_once_with(
            chat_id='123456',
            text="Test message"
        )

@pytest.mark.asyncio
async def test_start_bot_no_token():
    with patch.dict(os.environ, {}, clear=True):
        await start_bot()
        # Should not raise an exception

@pytest.mark.asyncio
async def test_start_bot_success():
    """Test starting the bot successfully."""
    mock_application = AsyncMock()
    with patch('app.telegram_bot.Application.builder') as mock_builder, \
         patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'test_token'}, clear=True), \
         patch('app.telegram_bot.asyncio.create_task') as mock_create_task:
        mock_builder.return_value.token.return_value.build.return_value = mock_application
        mock_create_task.return_value = AsyncMock()
        
        await start_bot()
        
        mock_application.add_handler.assert_called()
        mock_application.initialize.assert_called_once()
        mock_application.start.assert_called_once()
        mock_application.updater.start_polling.assert_called_once()

@pytest.mark.asyncio
async def test_stop_bot_no_application():
    """Test stopping bot when no application exists."""
    with patch('app.telegram_bot.application', None), \
         patch('app.telegram_bot.task_checker', None):
        await stop_bot()
