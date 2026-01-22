from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.language import Language, language_manager
from utils.logger import Logger


logger = Logger.get_logger(__name__)


async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection to user"""
    user_id = update.effective_user.id
    
    # Reset user state and set to language selection
    conversation_manager.clear_user(user_id)
    user = conversation_manager.get_user(user_id)
    user.update_state(BotState.LANGUAGE_SELECTION)
    
    # Create language selection keyboard
    keyboard = [
        [
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
            InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇪🇬 مصري", callback_data="lang_masri")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Get language prompt (default to English for this initial message)
    language_prompt = language_manager.get_text("language_prompt", Language.ENGLISH)
    
    if update.message:
        await update.message.reply_text(language_prompt, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(language_prompt, reply_markup=reply_markup)
    
    logger.info(f"User {user_id} shown language selection")


async def language_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    language_code = query.data.replace("lang_", "")
    
    # Convert to Language enum
    if language_code == "en":
        selected_language = Language.ENGLISH
    elif language_code == "masri":
        selected_language = Language.EGYPTIAN
    else:
        selected_language = Language.ARABIC
    
    # Save user's language preference
    conversation_manager.add_user_data(user_id, 'language', language_code)
    
    # Update state to collecting info
    conversation_manager.update_user_state(user_id, BotState.COLLECTING_INFO)
    
    # Get user's name for personalized welcome
    user_name = update.effective_user.first_name or "there"
    
    # CHECK DB FOR EXISTING USER DATA
    from bot.db_helper import get_user
    db_user = get_user(user_id)
    
    if db_user:
        # Load data into conversation manager
        conversation_manager.add_user_data(user_id, 'name', db_user['name'])
        conversation_manager.add_user_data(user_id, 'github', db_user['github'])
        if db_user.get('linkedin'):
            conversation_manager.add_user_data(user_id, 'linkedin', db_user['linkedin'])
        if db_user.get('portfolio'):
            conversation_manager.add_user_data(user_id, 'portfolio', db_user['portfolio'])
        if db_user.get('email'):
            conversation_manager.add_user_data(user_id, 'email', db_user['email'])
            
        # Skip info collection and go straight to experience
        # Send welcome message but with "Welcome back" context
        display_name = db_user.get('name') or update.effective_user.first_name or "there"
        welcome_text = language_manager.get_text("welcome_message", selected_language, name=display_name)
        
        # Change button to "Create New README" or similar context
        keyboard = [
            [InlineKeyboardButton(
                language_manager.get_text("lets_start_button", selected_language), 
                callback_data="start_collection"
            )],
            [InlineKeyboardButton(
                language_manager.get_text("how_it_works_button", selected_language), 
                callback_data="show_help"
            )]
        ]
        
    else:
        # New user flow
        welcome_text = language_manager.get_text("welcome_message", selected_language, name=user_name)
        
        keyboard = [
            [InlineKeyboardButton(
                language_manager.get_text("lets_start_button", selected_language), 
                callback_data="start_collection"
            )],
            [InlineKeyboardButton(
                language_manager.get_text("how_it_works_button", selected_language), 
                callback_data="show_help"
            )]
        ]
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    logger.info(f"User {user_id} selected language: {language_code}")


async def help_callback_with_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help callback with user's preferred language"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    # Get help text in user's language
    help_title = language_manager.get_text("help_title", user_language)
    help_steps = language_manager.get_text("help_steps", user_language)
    help_tips = language_manager.get_text("help_tips", user_language)
    
    help_text = f"{help_title}\n\n{help_steps}\n\n{help_tips}"
    
    # Create start button in user's language
    keyboard = [[InlineKeyboardButton(
        language_manager.get_text("lets_start_button", user_language), 
        callback_data="start_collection"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)
