from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.language import language_manager
from utils.logger import Logger


logger = Logger.get_logger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and begin conversation"""
    user_id = update.effective_user.id
    
    # Show language selection instead of direct start
    from bot.handlers.language_handler import show_language_selection
    await show_language_selection(update, context)
    logger.info(f"User {user_id} started the bot")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help callback"""
    from bot.handlers.language_handler import help_callback_with_language
    await help_callback_with_language(update, context)


async def start_collection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start collection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    conversation_manager.update_user_state(user_id, BotState.WAITING_NAME)
    
    prompt_text = language_manager.get_text("start_collection", user_language)
    
    await query.edit_message_text(prompt_text)
    logger.info(f"User {user_id} started info collection")