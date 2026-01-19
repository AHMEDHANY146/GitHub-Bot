from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.logger import Logger


logger = Logger.get_logger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and begin conversation"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "there"
    
    # Reset user state
    conversation_manager.clear_user(user_id)
    user = conversation_manager.get_user(user_id)
    user.update_state(BotState.COLLECTING_INFO)
    
    # Welcome message
    welcome_text = f"""
👋 Hello {user_name}! Welcome to the GitHub README Generator Bot!

I'll help you create a professional GitHub README.md file from your voice or text input.

Here's how it works:
1. 📝 Tell me your name and basic info
2. 🎤 Send a voice message or text about your experience
3. 🤖 I'll extract and structure your information
4. 📄 Generate a beautiful README with Devicon icons
5. 📦 Get it as a ZIP file ready for GitHub!

Ready to start? Let's begin with your name:
"""
    
    # Create inline keyboard
    keyboard = [
        [InlineKeyboardButton("🚀 Let's Start!", callback_data="start_collection")],
        [InlineKeyboardButton("ℹ️ How it Works", callback_data="show_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    logger.info(f"User {user_id} started the bot")


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help callback"""
    query = update.callback_query
    await query.answer()
    
    help_text = """
📖 How to Use This Bot

1. Start: Click "Let's Start!" to begin
2. Name: Tell me your full name
3. Your GitHub username: Share your GitHub username
4. Links (optional): LinkedIn, Portfolio, Email
5. Voice/Text: Send a voice message 🎤 or text 📝 describing:
   • Your experience and background
   • Technical skills and programming languages
   • Tools and platforms you use
   • Projects you've worked on

6. Review: I'll show you the extracted information
7. Confirm: Approve and get your README.md file

💡 Tips:
• Speak clearly and include specific technologies
• Mention frameworks, databases, and tools
• The more detail you provide, the better your README
• Voice messages work best for natural descriptions

🔧 Supported Languages:
Python, JavaScript, React, Docker, Git, AWS, and many more!

Ready? Click "Let's Start!" below!
"""
    
    keyboard = [[InlineKeyboardButton("🚀 Let's Start!", callback_data="start_collection")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_text, reply_markup=reply_markup)


async def start_collection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle start collection callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    conversation_manager.update_user_state(user_id, BotState.WAITING_NAME)
    
    prompt_text = """
Great! Let's start building your README.

First, what's your full name? 📝

Please type your name as you'd like it to appear on your GitHub profile.
"""
    
    await query.edit_message_text(prompt_text)
    logger.info(f"User {user_id} started info collection")