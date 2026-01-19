from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from bot.handlers.start_handler import start_handler, help_callback, start_collection_callback
from bot.handlers.info_handler import handle_text_input, skip_field_callback
from bot.handlers.voice_handler import voice_handler
from bot.handlers.confirm_handler import (
    approve_readme_callback, 
    edit_skills_callback,
    edit_contact_callback,
    add_tech_stack_callback,
    regenerate_readme_callback, 
    cancel_readme_callback
)
from bot.handlers.language_handler import language_selection_callback
from bot.handlers.rating_handler import (
    handle_rating_callback, 
    handle_feedback_callback, 
    handle_feedback_text
)
from utils.logger import Logger


logger = Logger.get_logger(__name__)


def setup_handlers(application: Application):
    """Setup all bot handlers and routing"""
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_command))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(help_callback, pattern="^show_help$"))
    application.add_handler(CallbackQueryHandler(start_collection_callback, pattern="^start_collection$"))
    application.add_handler(CallbackQueryHandler(skip_field_callback, pattern="^skip_"))
    application.add_handler(CallbackQueryHandler(approve_readme_callback, pattern="^approve_readme$"))
    application.add_handler(CallbackQueryHandler(edit_skills_callback, pattern="^edit_skills$"))
    application.add_handler(CallbackQueryHandler(edit_contact_callback, pattern="^edit_contact$"))
    application.add_handler(CallbackQueryHandler(add_tech_stack_callback, pattern="^add_tech_stack$"))
    application.add_handler(CallbackQueryHandler(regenerate_readme_callback, pattern="^regenerate_readme$"))
    application.add_handler(CallbackQueryHandler(cancel_readme_callback, pattern="^cancel_readme$"))
    application.add_handler(CallbackQueryHandler(language_selection_callback, pattern="^lang_"))
    
    # Rating and feedback handlers
    application.add_handler(CallbackQueryHandler(handle_rating_callback, pattern="^rating_"))
    application.add_handler(CallbackQueryHandler(handle_feedback_callback, pattern="^feedback_"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_feedback_text), group=1)  # Lower priority for feedback
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))
    
    logger.info("All handlers have been registered")


async def help_command(update, context):
    """Handle /help command"""
    help_text = """
🤖 GitHub README Bot Help

I help you create professional GitHub README.md files from your voice or text input!

How to use:
1. `/start` - Begin the conversation
2. Follow the prompts to provide your information
3. Send a voice message 🎤 or text 📝 about your experience
4. Review the extracted information
5. Get your README.md file as a ZIP package

Features:
• 🎤 Voice message transcription
• 🤖 AI-powered skill extraction
• 🎨 Devicon icons for technologies
• 📦 ZIP file with README + instructions
• ✏️ Edit and regenerate options

Supported Information:
• Name and contact details
• Technical skills and programming languages
• Development tools and platforms
• Professional experience summary

Tips for best results:
• Speak clearly in voice messages
• Mention specific technologies and frameworks
• Include details about projects and achievements
• Provide at least 50 characters of text description

Commands:
• `/start` - Start creating your README
• `/help` - Show this help message

Need more help? Just start the bot and follow the prompts!

🚀 Ready to create your professional GitHub profile?
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def error_handler(update, context):
    """Handle errors in the bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Get user language preference
    user_id = update.effective_user.id if update and update.effective_user else None
    user_language = None
    if user_id:
        try:
            from bot.states import conversation_manager
            user_language = conversation_manager.get_user_language(user_id)
        except:
            pass
    
    # Support message with developer contact (bilingual)
    if user_language == 'ar':
        support_message = """❌ حدث خطأ غير متوقع!

🔧 الدعم الفني:
تواصل مع المطور: @Ahmedhany146

سيساعدك في حل أي مشكلة تواجهها. لا تتردد في مراسلته!"""
        alert_message = "❌ حدث خطأ. تواصل مع @Ahmedhany146"
    else:
        support_message = """❌ An unexpected error occurred!

🔧 Technical Support:
Contact the developer: @Ahmedhany146

They will help you solve any issue you face. Don't hesitate to reach out!"""
        alert_message = "❌ An error occurred. Contact @Ahmedhany146"
    
    # Send user-friendly error message only if update is not None
    if update is not None:
        if update.message:
            await update.message.reply_text(support_message, parse_mode='Markdown')
        elif update.callback_query:
            try:
                await update.callback_query.answer(
                    alert_message,
                    show_alert=True
                )
            except:
                # If answering fails, try to edit the message
                try:
                    await update.callback_query.message.reply_text(support_message, parse_mode='Markdown')
                except:
                    # If all else fails, just log the error
                    logger.error("Could not send error message to user")


def setup_error_handlers(application: Application):
    """Setup error handlers"""
    application.add_error_handler(error_handler)
    logger.info("Error handlers have been registered")