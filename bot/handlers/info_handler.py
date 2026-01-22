from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.validators import Validators
from utils.language import language_manager
from utils.logger import Logger


logger = Logger.get_logger(__name__)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input during info collection"""
    user_id = update.effective_user.id
    user = conversation_manager.get_user(user_id)
    text = update.message.text.strip()
    user_language = conversation_manager.get_user_language(user_id)
    
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
    elif user.state == BotState.WAITING_CONTACT:
        await handle_contact_edit(update, text)
    elif user.state == BotState.WAITING_TECH_STACK:
        await handle_tech_stack_add(update, text)
    else:
        await update.message.reply_text(language_manager.get_text("not_sure", user_language))


async def handle_name_input(update: Update, name: str):
    """Handle name input"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_name(name):
        await update.message.reply_text(
            language_manager.get_text("invalid_name", user_language)
        )
        return
    
    # Save name
    conversation_manager.add_user_data(user_id, 'name', name)
    
    # Ask for GitHub username (now required)
    conversation_manager.update_user_state(user_id, BotState.WAITING_GITHUB)
    
    await update.message.reply_text(
        language_manager.get_text("name_saved", user_language, name=name)
    )
    logger.info(f"User {user_id} provided name: {name}")


async def handle_github_input(update: Update, github: str):
    """Handle GitHub username input (now required)"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_github_username(github):
        await update.message.reply_text(
            language_manager.get_text("invalid_github", user_language)
        )
        return
    
    # Save GitHub username
    conversation_manager.add_user_data(user_id, 'github', github)
    
    # Ask for LinkedIn (skip profile style selection)
    conversation_manager.update_user_state(user_id, BotState.WAITING_LINKEDIN)
    
    keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_linkedin")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        language_manager.get_text("github_saved", user_language, github=github),
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided GitHub: {github}")


async def handle_linkedin_input(update: Update, linkedin: str):
    """Handle LinkedIn URL input"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_linkedin_url(linkedin):
        keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_linkedin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            language_manager.get_text("invalid_linkedin", user_language),
            reply_markup=reply_markup
        )
        return
    
    # Save LinkedIn URL
    conversation_manager.add_user_data(user_id, 'linkedin', linkedin)
    
    # Ask for portfolio
    conversation_manager.update_user_state(user_id, BotState.WAITING_PORTFOLIO)
    
    keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_portfolio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        language_manager.get_text("linkedin_saved", user_language),
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided LinkedIn: {linkedin}")


async def handle_portfolio_input(update: Update, portfolio: str):
    """Handle portfolio URL input"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_url(portfolio):
        keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_portfolio")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            language_manager.get_text("invalid_portfolio", user_language),
            reply_markup=reply_markup
        )
        return
    
    # Save portfolio URL
    conversation_manager.add_user_data(user_id, 'portfolio', portfolio)
    
    # Ask for email
    conversation_manager.update_user_state(user_id, BotState.WAITING_EMAIL)
    
    keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        language_manager.get_text("portfolio_saved", user_language),
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} provided portfolio: {portfolio}")


async def handle_email_input(update: Update, email: str):
    """Handle email input"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_email(email):
        keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_email")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            language_manager.get_text("invalid_email", user_language),
            reply_markup=reply_markup
        )
        return
    
    # Save email
    conversation_manager.add_user_data(user_id, 'email', email)
    
    # Move to experience collection
    await start_experience_collection(update, user_id)


async def handle_experience_text(update: Update, text: str):
    """Handle experience text input"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    if not Validators.validate_text_length(text, min_length=50):
        await update.message.reply_text(
            language_manager.get_text("invalid_experience", user_language)
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
    user_language = conversation_manager.get_user_language(user_id)
    
    # Determine which field to skip and move to next
    if user.state == BotState.WAITING_GITHUB:
        await start_experience_collection(update, user_id)
    elif user.state == BotState.WAITING_LINKEDIN:
        conversation_manager.update_user_state(user_id, BotState.WAITING_PORTFOLIO)
        keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_portfolio")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            language_manager.get_text("skipped_linkedin", user_language),
            reply_markup=reply_markup
        )
    elif user.state == BotState.WAITING_PORTFOLIO:
        conversation_manager.update_user_state(user_id, BotState.WAITING_EMAIL)
        keyboard = [[InlineKeyboardButton(language_manager.get_text("skip_button", user_language), callback_data="skip_email")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            language_manager.get_text("skipped_portfolio", user_language),
            reply_markup=reply_markup
        )
    elif user.state == BotState.WAITING_EMAIL:
        await start_experience_collection(update, user_id)


async def start_experience_collection(update: Update, user_id: int):
    """Start collecting experience information"""
    conversation_manager.update_user_state(user_id, BotState.WAITING_VOICE)
    
    name = conversation_manager.get_user_data(user_id, 'name', 'there')
    user_language = conversation_manager.get_user_language(user_id)
    
    experience_text = language_manager.get_text("experience_prompt", user_language, name=name)
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(experience_text)
    else:
        await update.message.reply_text(experience_text)
    
    logger.info(f"User {user_id} moved to experience collection")


async def start_processing(update: Update, user_id: int):
    """Start processing the collected information"""
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    user_language = conversation_manager.get_user_language(user_id)
    processing_text = language_manager.get_text("processing", user_language)
    
    if isinstance(update, Update) and update.callback_query:
        await update.callback_query.edit_message_text(processing_text)
    else:
        await update.message.reply_text(processing_text)
    
    logger.info(f"User {user_id} moved to processing state")
    
    # Trigger processing (this would be handled by the main bot logic)
    from bot.handlers.voice_handler import process_user_data
    await process_user_data(update, user_id)


async def handle_contact_edit(update: Update, text: str):
    """Handle contact information editing"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    try:
        # Parse contact information from text
        lines = text.strip().split('\n')
        updated_fields = []
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Update each field with validation
                if key in ['name', 'github', 'linkedin', 'portfolio', 'email']:
                    if key == 'name' and Validators.validate_name(value):
                        conversation_manager.add_user_data(user_id, key, value)
                        updated_fields.append(f"✅ {key.title()}: {value}")
                    elif key == 'github' and Validators.validate_github_username(value):
                        conversation_manager.add_user_data(user_id, key, value)
                        updated_fields.append(f"✅ {key.title()}: {value}")
                    elif key == 'linkedin' and Validators.validate_linkedin_url(value):
                        conversation_manager.add_user_data(user_id, key, value)
                        updated_fields.append(f"✅ {key.title()}: {value}")
                    elif key == 'portfolio' and Validators.validate_url(value):
                        conversation_manager.add_user_data(user_id, key, value)
                        updated_fields.append(f"✅ {key.title()}: {value}")
                    elif key == 'email' and Validators.validate_email(value):
                        conversation_manager.add_user_data(user_id, key, value)
                        updated_fields.append(f"✅ {key.title()}: {value}")
                    else:
                        updated_fields.append(f"❌ Invalid {key.title()}: {value}")
        
        if updated_fields:
            result_text = language_manager.get_text(
                "contact_updated_success", 
                user_language, 
                updated_fields="\n".join(updated_fields)
            )
            
            await update.message.reply_text(result_text)
            
            # Re-process the data with updated information
            await start_processing(update, user_id)
        else:
            await update.message.reply_text(language_manager.get_text("contact_updated_error", user_language))
            
    except Exception as e:
        logger.error(f"Error processing contact edit: {e}")
        await update.message.reply_text(language_manager.get_text("contact_error", user_language))
    
    logger.info(f"User {user_id} edited contact information")


async def handle_tech_stack_add(update: Update, text: str):
    """Handle adding tech stack items"""
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    try:
        # Parse tech stack items from text
        import re
        # Split by commas and clean up
        items = [item.strip() for item in re.split(r'[,，\n]+', text) if item.strip()]
        
        if not items:
            await update.message.reply_text(language_manager.get_text("tech_stack_error_empty", user_language))
            return
        
        # Get current structured data
        user = conversation_manager.get_user(user_id)
        structured_data = user.get_data('structured_data', {})
        
        # Add new items to appropriate categories
        current_skills = structured_data.get('skills', [])
        current_tools = structured_data.get('tools', [])
        current_languages = structured_data.get('languages', [])
        
        added_skills = []
        added_tools = []
        added_languages = []
        
        # Categorize new items
        for item in items:
            item_lower = item.lower()
            # Improved categorization matching the markdown generator
            if any(lang in item_lower for lang in ['python', 'javascript', 'java', 'c++', 'c#', 'typescript', 'go', 'rust', 'php', 'swift', 'kotlin', 'ruby', 'scala', 'r', 'matlab', 'html', 'css']):
                if item not in current_languages:
                    current_languages.append(item)
                    added_languages.append(item)
            elif any(keyword in item_lower for keyword in ['tensorflow', 'pytorch', 'keras', 'scikit', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'opencv', 'nltk', 'spacy', 'react', 'vue', 'angular', 'django', 'flask', 'spring', 'laravel', 'express', 'next', 'tailwind', 'bootstrap', 'node', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'power bi', 'tableau', 'excel', 'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'rag', 'chatbot', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'data science', 'ai', 'artificial intelligence']):
                if item not in current_skills:
                    current_skills.append(item)
                    added_skills.append(item)
            else:
                if item not in current_tools:
                    current_tools.append(item)
                    added_tools.append(item)
        
        # Update structured data
        structured_data['skills'] = current_skills
        structured_data['tools'] = current_tools
        structured_data['languages'] = current_languages
        user.add_data('structured_data', structured_data)
        
        # Show what was added
        details = ""
        if added_languages:
            details += f"💻 Languages: {', '.join(added_languages)}\n"
        if added_skills:
            details += f"🛠️ Skills: {', '.join(added_skills)}\n"
        if added_tools:
            details += f"🔧 Tools: {', '.join(added_tools)}\n"
            
        result_text = language_manager.get_text("tech_stack_updated", user_language, details=details)
        
        await update.message.reply_text(result_text)
        
        # Re-process the data with updated tech stack
        await start_processing(update, user_id)
        
    except Exception as e:
        logger.error(f"Error processing tech stack addition: {e}")
        await update.message.reply_text(language_manager.get_text("tech_stack_error", user_language))
    
    logger.info(f"User {user_id} added tech stack items")