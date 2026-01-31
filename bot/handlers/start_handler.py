from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.language import language_manager
from utils.logger import Logger
from bot.db_helper import save_user


logger = Logger.get_logger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and begin conversation"""
    user_id = update.effective_user.id
    
    # Save user to database
    save_user(telegram_id=user_id, name=update.effective_user.first_name)
    
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
    
    # CHECK IF DATA WAS PRE-LOADED
    user_data = conversation_manager.get_user(user_id)
    if user_data.get_data('name') and user_data.get_data('github'):
        # Data exists, skip to experience collection
        conversation_manager.update_user_state(user_id, BotState.WAITING_VOICE) # Or WAITING_TEXT
        
        name = user_data.get_data('name')
        prompt_text = language_manager.get_text("experience_prompt", user_language, name=name)
        
        logger.info(f"User {user_id} skipped to experience collection (data pre-loaded)")
    else:
        # No data or incomplete data, start normal flow
        # If they have a name but no github, it will start from WAITING_NAME but handle_name_input will move them forward.
        # Actually, it's better to be specific.
        if not user_data.get_data('name'):
            conversation_manager.update_user_state(user_id, BotState.WAITING_NAME)
            prompt_text = language_manager.get_text("start_collection", user_language)
        else:
            conversation_manager.update_user_state(user_id, BotState.WAITING_GITHUB)
            prompt_text = language_manager.get_text("name_saved", user_language, name=user_data.get_data('name'))
            
        logger.info(f"User {user_id} started/continued info collection")
    
    await query.edit_message_text(prompt_text)