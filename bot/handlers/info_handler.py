from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.validators import Validators
from utils.logger import Logger


logger = Logger.get_logger(__name__)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input during info collection"""
    user_id = update.effective_user.id
    user = conversation_manager.get_user(user_id)
    text = update.message.text.strip()
    
    # Handle based on current state
    if user.state == BotState.WAITING_NAME:
        await handle_name_input(update, text)
    elif user.state == BotState.WAITING_GITHUB:
        await handle_github_input(update, text)
    elif user.state == BotState.WAITING_LINKEDIN:
        await handle_linkedin_input(update, text)
    elif user.state == BotState.WAITING_PORTFOLIO:
        await handle_portfolio_input(update, text)
    elif user.state == BotState.WAITING_EMAIL:
        await handle_email_input(update, text)
    elif user.state == BotState.WAITING_TEXT:
        await handle_experience_text(update, text)
    else:
        await update.message.reply_text("I'm not sure what you want to do. Please use /start to begin.")


async def handle_name_input(update: Update, name: str):
    """Handle name input"""
    user_id = update.effective_user.id
    
    if not Validators.validate_name(name):
        await update.message.reply_text(
            "❌ Please enter a valid name (2-50 characters, letters only).\n"
            "What's your full name?"
        )
        return
    
    # Save name
    conversation_manager.add_user_data(user_id, 'name', name)
    
    # Ask for GitHub username (now required)
    conversation_manager.update_user_state(user_id, BotState.WAITING_GITHUB)
    
    await update.message.reply_text(
        f"✅ Great! Your name is: {name}\n\n"
        "What's your GitHub username? (required)\n"
        "This will be used for GitHub stats and profile links."
    )
    logger.info(f"User {user_id} provided name: {name}")


async def handle_github_input(update: Update, github: str):
    """Handle GitHub username input (now required)"""
    user_id = update.effective_user.id
    
    if not Validators.validate_github_username(github):
        await update.message.reply_text(
            "❌ Please enter a valid GitHub username.\n"
            "GitHub usernames are 1-39 characters, alphanumeric and hyphens only.\n"
            "What's your GitHub username? (required)"
        )
        return
    
    # Save GitHub username
    conversation_manager.add_user_data(user_id, 'github', github)
    
    # Ask for profile style
    conversation_manager.update_user_state(user_id, BotState.WAITING_PROFILE_STYLE)
    
    keyboard = [
        [InlineKeyboardButton("🎯 Modern", callback_data="style_modern")],
        [InlineKeyboardButton("⚡ Minimal", callback_data="style_minimal")],
        [InlineKeyboardButton("🔥 Bold", callback_data="style_bold")],
        [InlineKeyboardButton("💡 Creative", callback_data="style_creative")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ GitHub username saved: {github}\n\n"
        "Choose your profile style:",
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided GitHub: {github}")


async def handle_profile_style_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile style selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    style_map = {
        "style_modern": "modern",
        "style_minimal": "minimal", 
        "style_bold": "bold",
        "style_creative": "creative"
    }
    
    selected_style = style_map.get(query.data, "modern")
    conversation_manager.add_user_data(user_id, 'profile_style', selected_style)
    
    # Ask for LinkedIn
    conversation_manager.update_user_state(user_id, BotState.WAITING_LINKEDIN)
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data="skip_linkedin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"✅ Profile style selected: {selected_style.title()}\n\n"
        "What's your LinkedIn profile URL? (optional)",
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} selected profile style: {selected_style}")


async def handle_linkedin_input(update: Update, linkedin: str):
    """Handle LinkedIn URL input"""
    user_id = update.effective_user.id
    
    if not Validators.validate_linkedin_url(linkedin):
        await update.message.reply_text(
            "❌ Please enter a valid LinkedIn URL.\n"
            "Example: https://linkedin.com/in/yourname\n"
            "What's your LinkedIn URL? (or click Skip)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭️ Skip", callback_data="skip_linkedin")]])
        )
        return
    
    # Save LinkedIn URL
    conversation_manager.add_user_data(user_id, 'linkedin', linkedin)
    
    # Ask for portfolio
    conversation_manager.update_user_state(user_id, BotState.WAITING_PORTFOLIO)
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data="skip_portfolio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ LinkedIn profile saved\n\n"
        "What's your portfolio website URL? (optional)",
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided LinkedIn: {linkedin}")


async def handle_portfolio_input(update: Update, portfolio: str):
    """Handle portfolio URL input"""
    user_id = update.effective_user.id
    
    if not Validators.validate_url(portfolio):
        await update.message.reply_text(
            "❌ Please enter a valid portfolio URL.\n"
            "Example: https://yourname.github.io or https://yourportfolio.com\n"
            "What's your portfolio URL? (or click Skip)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭️ Skip", callback_data="skip_portfolio")]])
        )
        return
    
    # Save portfolio URL
    conversation_manager.add_user_data(user_id, 'portfolio', portfolio)
    
    # Ask for email
    conversation_manager.update_user_state(user_id, BotState.WAITING_EMAIL)
    
    keyboard = [[InlineKeyboardButton("⏭️ Skip", callback_data="skip_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"✅ Portfolio saved\n\n"
        "What's your email address? (optional)",
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided portfolio: {portfolio}")


async def handle_email_input(update: Update, email: str):
    """Handle email input"""
    user_id = update.effective_user.id
    
    if not Validators.validate_email(email):
        await update.message.reply_text(
            "❌ Please enter a valid email address.\n"
            "What's your email address? (or click Skip)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭️ Skip", callback_data="skip_email")]])
        )
        return
    
    # Save email
    conversation_manager.add_user_data(user_id, 'email', email)
    
    # Move to experience collection
    await start_experience_collection(update, user_id)


async def handle_experience_text(update: Update, text: str):
    """Handle experience text input"""
    user_id = update.effective_user.id
    
    if not Validators.validate_text_length(text, min_length=50):
        await update.message.reply_text(
            "❌ Please provide more details about your experience (at least 50 characters).\n\n"
            "Tell me about:\n"
            "• Your background and experience\n"
            "• Technical skills and programming languages\n"
            "• Tools and platforms you use\n"
            "• Projects you've worked on\n\n"
            "You can also send a voice message instead!"
        )
        return
    
    # Save experience text
    conversation_manager.add_user_data(user_id, 'experience_text', text)
    
    # Move to processing
    await start_processing(update, user_id)
    logger.info(f"User {user_id} provided experience text")


async def skip_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skip field callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = conversation_manager.get_user(user_id)
    
    # Determine which field to skip and move to next
    if user.state == BotState.WAITING_GITHUB:
        await start_experience_collection(update, user_id)
    elif user.state == BotState.WAITING_LINKEDIN:
        conversation_manager.update_user_state(user_id, BotState.WAITING_PORTFOLIO)
        await query.edit_message_text(
            "✅ Skipped LinkedIn\n\n"
            "What's your portfolio website URL? (optional)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭️ Skip", callback_data="skip_portfolio")]])
        )
    elif user.state == BotState.WAITING_PORTFOLIO:
        conversation_manager.update_user_state(user_id, BotState.WAITING_EMAIL)
        await query.edit_message_text(
            "✅ Skipped portfolio\n\n"
            "What's your email address? (optional)",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭️ Skip", callback_data="skip_email")]])
        )
    elif user.state == BotState.WAITING_EMAIL:
        await start_experience_collection(update, user_id)


async def start_experience_collection(update: Update, user_id: int):
    """Start collecting experience information"""
    conversation_manager.update_user_state(user_id, BotState.WAITING_VOICE)
    
    name = conversation_manager.get_user_data(user_id, 'name', 'there')
    
    experience_text = f"""
Perfect! Thanks {name}! 🎉

Now, tell me about your experience and skills. You can:

🎤 Send a voice message
📝 Type a text description

Tell me about:
• Your professional background
• Programming languages and frameworks
• Tools and platforms you work with
• Notable projects or achievements

The more detail you provide, the better your README will be!
"""
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(experience_text)
    else:
        await update.message.reply_text(experience_text)
    
    logger.info(f"User {user_id} moved to experience collection")


async def start_processing(update: Update, user_id: int):
    """Start processing the collected information"""
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    processing_text = """
🔄 Processing your information...

I'm analyzing your experience and extracting:
• Technical skills
• Programming languages  
• Tools and platforms
• Professional summary

This will take a few moments...
"""
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(processing_text)
    else:
        await update.message.reply_text(processing_text)
    
    logger.info(f"User {user_id} moved to processing state")
    
    # Trigger processing (this would be handled by the main bot logic)
    from bot.handlers.voice_handler import process_user_data
    await process_user_data(update, user_id)