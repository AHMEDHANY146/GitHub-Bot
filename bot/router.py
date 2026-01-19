from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram.ext import filters
from bot.handlers.start_handler import start_handler, help_callback, start_collection_callback
from bot.handlers.info_handler import handle_text_input, skip_field_callback, handle_profile_style_callback
from bot.handlers.voice_handler import voice_handler
from bot.handlers.confirm_handler import (
    approve_readme_callback, 
    edit_skills_callback, 
    regenerate_readme_callback, 
    cancel_readme_callback
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
    application.add_handler(CallbackQueryHandler(handle_profile_style_callback, pattern="^style_"))
    application.add_handler(CallbackQueryHandler(approve_readme_callback, pattern="^approve_readme$"))
    application.add_handler(CallbackQueryHandler(edit_skills_callback, pattern="^edit_skills$"))
    application.add_handler(CallbackQueryHandler(regenerate_readme_callback, pattern="^regenerate_readme$"))
    application.add_handler(CallbackQueryHandler(cancel_readme_callback, pattern="^cancel_readme$"))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))
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
    
    # Send user-friendly error message only if update is not None
    if update is not None:
        if update.message:
            await update.message.reply_text(
                "❌ An unexpected error occurred. Please try again or contact support."
            )
        elif update.callback_query:
            try:
                await update.callback_query.answer(
                    "❌ An error occurred. Please try again.",
                    show_alert=True
                )
            except:
                # If answering fails, try to edit the message
                try:
                    await update.callback_query.message.reply_text(
                        "❌ An unexpected error occurred. Please try again or contact support."
                    )
                except:
                    # If all else fails, just log the error
                    logger.error("Could not send error message to user")


def setup_error_handlers(application: Application):
    """Setup error handlers"""
    application.add_error_handler(error_handler)
    logger.info("Error handlers have been registered")