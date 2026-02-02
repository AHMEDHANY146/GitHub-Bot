from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.logger import Logger
from utils.language import language_manager, Language
from helpers.config import get_settings
from bot.db_helper import save_rating

logger = Logger.get_logger(__name__)
settings = get_settings()


async def show_rating_prompt(update, context):
    """Show rating prompt to user after successful README generation"""
    query = update.callback_query
    if query:
        await query.answer()
    
    # Get user language preference
    user_id = update.effective_user.id
    user_language = None
    try:
        from bot.states import conversation_manager
        user_language_code = conversation_manager.get_user_language(user_id)
        user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    except:
        user_language = Language.ENGLISH
    
    # Use language manager for bilingual rating text
    rating_text = language_manager.get_text("rating_prompt", user_language)
    skip_text = language_manager.get_text("rating_skip", user_language)
    
    keyboard = [
        [
            InlineKeyboardButton("⭐⭐⭐⭐⭐", callback_data="rating_5"),
            InlineKeyboardButton("⭐⭐⭐⭐", callback_data="rating_4")
        ],
        [
            InlineKeyboardButton("⭐⭐⭐", callback_data="rating_3"),
            InlineKeyboardButton("⭐⭐", callback_data="rating_2")
        ],
        [
            InlineKeyboardButton("⭐", callback_data="rating_1"),
            InlineKeyboardButton(skip_text, callback_data="rating_skip")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Use update.effective_message instead of query.message for broader compatibility
    await update.effective_message.reply_text(rating_text, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_rating_callback(update, context):
    """Handle rating selection and show feedback/support options"""
    query = update.callback_query
    await query.answer()
    
    rating = query.data.split('_')[1]
    
    # Get user language preference
    user_id = update.effective_user.id
    user_language = None
    try:
        from bot.states import conversation_manager
        user_language_code = conversation_manager.get_user_language(user_id)
        user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    except:
        user_language = Language.ENGLISH
    
    if rating == 'skip':
        text = language_manager.get_text("rating_skip_message", user_language)
        await query.message.edit_text(text)
        return
    
    # Convert rating to stars
    stars = "⭐" * int(rating)
    
    # Save rating to database
    session_id = context.user_data.get('session_id')
    save_rating(user_id, int(rating), session_id=session_id)
    
    # Notify developer about rating
    try:
        user_name = update.effective_user.first_name
        dev_message = f"🌟 New Rating!\nUser: {user_name} (ID: {user_id})\nRating: {stars}"
        await context.bot.send_message(chat_id=settings.DEVELOPER_CHAT_ID, text=dev_message)
    except Exception as e:
        logger.error(f"Failed to notify developer about rating: {e}")
    
    feedback_text = language_manager.get_text("rating_feedback_button", user_language)
    end_text = language_manager.get_text("rating_end_button", user_language)
    support_text = language_manager.get_text("rating_support_button", user_language)
    contact_text = language_manager.get_text("rating_contact_button", user_language)
    
    if rating == '5':
        message = language_manager.get_text("rating_thanks_5", user_language, stars=stars)
        
        keyboard = [
            [
                InlineKeyboardButton(feedback_text, callback_data="feedback_yes"),
                InlineKeyboardButton(end_text, callback_data="feedback_end")
            ],
            [
                InlineKeyboardButton(support_text, url="https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH")
            ]
        ]
    elif rating in ['4', '3']:
        message = language_manager.get_text("rating_thanks_4_3", user_language, stars=stars)
        
        keyboard = [
            [
                InlineKeyboardButton(feedback_text, callback_data="feedback_yes"),
                InlineKeyboardButton(end_text, callback_data="feedback_end")
            ],
            [
                InlineKeyboardButton(support_text, url="https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH")
            ]
        ]
    else:  # rating 1 or 2
        message = language_manager.get_text("rating_thanks_1_2", user_language, stars=stars)
        
        keyboard = [
            [
                InlineKeyboardButton(contact_text, url="https://t.me/Ahmedhany146"),
                InlineKeyboardButton(end_text, callback_data="feedback_end")
            ]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_feedback_callback(update, context):
    """Handle feedback collection"""
    query = update.callback_query
    await query.answer()
    
    # Get user language preference
    user_id = update.effective_user.id
    user_language = None
    try:
        from bot.states import conversation_manager
        user_language_code = conversation_manager.get_user_language(user_id)
        user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    except:
        user_language = Language.ENGLISH
    
    if query.data == "feedback_end":
        text = language_manager.get_text("rating_end_message", user_language)
        await query.message.edit_text(text)
        return
    
    # Start feedback collection
    feedback_text = language_manager.get_text("feedback_prompt", user_language)
    
    # Store feedback state in user_data
    context.user_data['awaiting_feedback'] = True
    
    await query.message.edit_text(feedback_text, parse_mode='Markdown')


async def handle_feedback_text(update, context):
    """Handle text feedback from user"""
    if context.user_data.get('awaiting_feedback'):
        feedback_text = update.message.text
        
        # Get user language preference
        user_id = update.effective_user.id
        user_language = None
        try:
            from bot.states import conversation_manager
            user_language_code = conversation_manager.get_user_language(user_id)
            user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
        except:
            user_language = Language.ENGLISH
        
        # Log the feedback
        logger.info(f"User feedback received: {feedback_text}")
        
        # Save feedback to database (update the existing rating with feedback)
        session_id = context.user_data.get('session_id')
        save_rating(user_id, 5, feedback_text=feedback_text, session_id=session_id)  # Default 5 stars if feedback provided
        
        # Notify developer about feedback
        try:
            user_name = update.effective_user.first_name
            dev_message = f"💬 New Feedback!\nUser: {user_name} (ID: {user_id})\nMessage: {feedback_text}"
            await context.bot.send_message(chat_id=settings.DEVELOPER_CHAT_ID, text=dev_message)
        except Exception as e:
            logger.error(f"Failed to notify developer about feedback: {e}")
        
        # Thank you message
        thank_you_text = language_manager.get_text("feedback_thanks", user_language)
        
        support_text = language_manager.get_text("rating_support_button", user_language)
        
        keyboard = [
            [
                InlineKeyboardButton(support_text, url="https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(thank_you_text, reply_markup=reply_markup, parse_mode='Markdown')
        
        # Clear feedback state
        del context.user_data['awaiting_feedback']
