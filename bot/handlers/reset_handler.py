from telegram import Update
from telegram.ext import ContextTypes
from bot.states import conversation_manager, BotState
from utils.language import language_manager
from utils.logger import Logger

logger = Logger.get_logger(__name__)

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fully reset user session and data"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    # Perform reset
    conversation_manager.clear_user(user_id)
    
    # Log reset
    logger.info(f"User {user_id} manually reset their session")
    
    # Notify user (Bilingual or based on preferred)
    # Since we cleared language too, we use default or what they had
    from utils.language import Language
    msg = "✅ Session has been fully reset. Send /start to begin a new README!"
    if user_language == Language.ARABIC:
        msg = "✅ تم إعادة ضبط الجلسة بنجاح. أرسل /start للبدء من جديد!"
    elif user_language == Language.EGYPTIAN:
        msg = "✅ الجلسة اتصفرت يا بطل. ابعت /start عشان نبدأ من جديد! 😎"
        
    await update.message.reply_text(msg)
