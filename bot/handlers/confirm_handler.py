from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os
import tempfile
import zipfile
from io import BytesIO
from bot.states import BotState, conversation_manager
from utils.language import language_manager, Language
from utils.logger import Logger
from bot.handlers import voice_handler
from bot.handlers.rating_handler import show_rating_prompt
from bot.db_helper import save_user, create_readme_session, complete_readme_session

logger = Logger.get_logger(__name__)

async def show_confirmation(update: Update, user_id: int):
    """Show confirmation with extracted information"""
    user = conversation_manager.get_user(user_id)
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    structured_data = user.get_data('structured_data', {})
    
    # Format extracted information for display
    confirmation_text = format_confirmation_text(structured_data, user, user_language)
    
    # Create inline keyboard for confirmation with more editing options
    keyboard = [
        [
            InlineKeyboardButton(language_manager.get_text("approve_button", user_language), callback_data="approve_readme"),
            InlineKeyboardButton(language_manager.get_text("add_tech_button", user_language), callback_data="add_tech_stack")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("edit_contact_button", user_language), callback_data="edit_contact"),
            InlineKeyboardButton(language_manager.get_text("regenerate_button", user_language), callback_data="regenerate_readme")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("cancel_button", user_language), callback_data="cancel_readme")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(confirmation_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
    
    logger.info(f"Showing confirmation for user {user_id}")


def format_confirmation_text(structured_data: dict, user, user_language) -> str:
    """Format the confirmation text with extracted information"""
    name = structured_data.get('name', 'Your Name')
    summary = structured_data.get('summary', '')
    skills = structured_data.get('skills', [])
    tools = structured_data.get('tools', [])
    languages = structured_data.get('languages', [])
    currently_working_on = structured_data.get('currently_working_on', '')
    currently_learning = structured_data.get('currently_learning', '')
    open_to = structured_data.get('open_to', '')
    fun_fact = structured_data.get('fun_fact', '')
    
    # Get user's contact info
    github = user.get_data('github')
    linkedin = user.get_data('linkedin')
    portfolio = user.get_data('portfolio')
    email = user.get_data('email')
    
    # Check if Arabic or Masri for correct list formatting (RTL)
    is_rtl = user_language == Language.ARABIC or user_language == Language.EGYPTIAN
    
    # Format lists
    skills_text = format_skill_list_improved(skills, user_language)
    tools_text = format_skill_list_improved(tools, user_language)
    languages_text = format_skill_list_improved(languages, user_language)
    
    # Build contact string
    contact_parts = []
    if github: contact_parts.append(f"• GitHub: {github}")
    if linkedin: contact_parts.append(f"• LinkedIn: {linkedin}")
    if portfolio: contact_parts.append(f"• Portfolio: {portfolio}")
    if email: contact_parts.append(f"• Email: {email}")
    contact_info = "\n".join(contact_parts)
    
    # Build skills section
    section_parts = []
    
    # Combine all tech stack items
    all_tech = []
    if languages: all_tech.extend(languages)
    if skills: all_tech.extend(skills)
    if tools: all_tech.extend(tools)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tech = []
    for item in all_tech:
        item_lower = item.lower().strip()
        if item_lower not in seen:
            seen.add(item_lower)
            unique_tech.append(item)
    
    if unique_tech:
        title = language_manager.get_text("header_tech_stack", user_language)
        tech_text = format_skill_list_improved(unique_tech, user_language)
        section_parts.append(f"{title} ({len(unique_tech)}):\n{tech_text}")
        
    skills_section = "\n\n".join(section_parts)
    
    # Build additional info
    additional_parts = []
    if currently_working_on:
        label = language_manager.get_text("label_working_on", user_language)
        additional_parts.append(f"• {label} {currently_working_on}")
    if currently_learning:
        label = language_manager.get_text("label_learning", user_language)
        additional_parts.append(f"• {label} {currently_learning}")
    if open_to:
        label = language_manager.get_text("label_open_to", user_language)
        additional_parts.append(f"• {label} {open_to}")
    if fun_fact:
        label = language_manager.get_text("label_fun_fact", user_language)
        additional_parts.append(f"• {label} {fun_fact}")
        
    additional_info = "\n".join(additional_parts) if additional_parts else language_manager.get_text("text_none", user_language)
    
    return language_manager.get_text(
        "confirmation_text",
        user_language,
        name=name,
        contact_info=contact_info,
        summary=summary,
        skills_section=skills_section,
        additional_info=additional_info
    )


def format_skill_list_improved(skills: list, user_language) -> str:
    """Format a list of skills for display - improved version"""
    if not skills:
        return language_manager.get_text("text_none", user_language)
    
    # Format skills in a clean grid-like display
    formatted_skills = [skill.title() for skill in skills]
    
    # Show all skills, formatted nicely
    if len(formatted_skills) <= 15:
        # Show in rows of 3-4 skills
        rows = []
        for i in range(0, len(formatted_skills), 3):
            row_skills = formatted_skills[i:i+3]
            rows.append("  " + " • ".join(row_skills))
        return "\n".join(rows)
    else:
        # Show first 12 with indicator
        shown = formatted_skills[:12]
        remaining = len(formatted_skills) - 12
        rows = []
        for i in range(0, len(shown), 3):
            row_skills = shown[i:i+3]
            rows.append("  " + " • ".join(row_skills))
        
        more_text = language_manager.get_text("text_and_more", user_language, count=remaining)
        rows.append(f"  📌 {more_text}")
        return "\n".join(rows)


def format_skill_list(skills: list) -> str:
    """Format a list of skills for display - legacy version"""
    if not skills:
        return "None"
    
    # Show all skills if 10 or less, otherwise show first 10 with indicator
    if len(skills) <= 10:
        return ', '.join([f"• {skill.title()}" for skill in skills])
    else:
        shown_skills = skills[:10]
        remaining = len(skills) - 10
        return ', '.join([f"• {skill.title()}" for skill in shown_skills]) + f"\n• ... and {remaining} more skills"


async def approve_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle approve README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Update state to completed
    conversation_manager.update_user_state(user_id, BotState.COMPLETED)
    
    # Generate and send ZIP file
    await generate_and_send_zip(update, context, user_id)
    
    logger.info(f"User {user_id} approved README generation")


async def edit_skills_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit skills callback - show skill selection screen"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Show skill selection screen
    from bot.handlers.skill_handler import show_skill_selection
    await show_skill_selection(update, user_id)
    
    logger.info(f"User {user_id} chose to edit skills (selection mode)")


async def edit_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit contact information callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Show sub-menu for granular editing
    keyboard = [
        [
            InlineKeyboardButton(language_manager.get_text("edit_name_button", user_language), callback_data="edit_basic_name"),
            InlineKeyboardButton(language_manager.get_text("edit_github_button", user_language), callback_data="edit_basic_github")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("edit_linkedin_button", user_language), callback_data="edit_basic_linkedin"),
            InlineKeyboardButton(language_manager.get_text("edit_portfolio_button", user_language), callback_data="edit_basic_portfolio")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("edit_email_button", user_language), callback_data="edit_basic_email")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("back_to_confirmation", user_language), callback_data="back_to_confirm")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        language_manager.get_text("edit_contact_menu_title", user_language),
        reply_markup=reply_markup
    )
    logger.info(f"User {user_id} opened granular edit menu")


async def edit_basic_field_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle individual field edit button press"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    field = query.data.replace("edit_basic_", "")
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Map fields to states and prompts
    field_map = {
        "name": (BotState.WAITING_EDIT_NAME, "start_collection"),
        "github": (BotState.WAITING_EDIT_GITHUB, "name_saved"), # name_saved prompt asks for github
        "linkedin": (BotState.WAITING_EDIT_LINKEDIN, "github_saved"), # github_saved asks for linkedin
        "portfolio": (BotState.WAITING_EDIT_PORTFOLIO, "linkedin_saved"),
        "email": (BotState.WAITING_EDIT_EMAIL, "portfolio_saved")
    }
    
    if field in field_map:
        state, prompt_key = field_map[field]
        conversation_manager.update_user_state(user_id, state)
        
        # Determine the correct prompt text (some need params like name)
        if prompt_key == "name_saved":
            name = conversation_manager.get_user_data(user_id, 'name', 'there')
            text = language_manager.get_text(prompt_key, user_language, name=name)
        elif prompt_key == "github_saved":
            github = conversation_manager.get_user_data(user_id, 'github', 'user')
            text = language_manager.get_text(prompt_key, user_language, github=github)
        else:
            text = language_manager.get_text(prompt_key, user_language)
            
        await query.edit_message_text(text)
        logger.info(f"User {user_id} editing field: {field}")


async def back_to_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to confirmation screen"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    conversation_manager.update_user_state(user_id, BotState.CONFIRMATION)
    await show_confirmation(update, user_id)


async def add_tech_stack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add tech stack callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Show interactive skill selection instead of text prompt
    from bot.handlers.skill_handler import show_skill_selection
    await show_skill_selection(update, user_id)
    logger.info(f"User {user_id} chose to add tech stack items")


async def regenerate_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regenerate README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Move back to processing
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    await query.edit_message_text(language_manager.get_text("regenerate_message", user_language))
    
    # Re-process the data
    from bot.handlers.voice_handler import process_user_data
    await process_user_data(update, user_id)
    
    logger.info(f"User {user_id} chose to regenerate README")


async def cancel_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Clear user data
    conversation_manager.clear_user(user_id)
    
    cancel_text = language_manager.get_text("cancel_message", user_language)
    
    await query.edit_message_text(cancel_text)
    logger.info(f"User {user_id} cancelled README generation")


async def generate_and_send_zip(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Generate ZIP file with README and send to user"""
    try:
        user = conversation_manager.get_user(user_id)
        readme_content = user.get_data('readme_content')
        structured_data = user.get_data('structured_data', {})
        
        if not readme_content:
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.message.reply_text("❌ No README content found.")
            else:
                await update.message.reply_text("❌ No README content found.")
            return
        
        # Save to database
        telegram_id = update.effective_user.id
        
        # Update user info in database
        save_user(
            telegram_id=telegram_id,
            name=user.get_data('name'),
            github_username=user.get_data('github'),
            linkedin_url=user.get_data('linkedin'),
            portfolio_url=user.get_data('portfolio'),
            email=user.get_data('email')
        )
        
        # Create session and save skills
        session_id = create_readme_session(telegram_id, user.get_data('raw_input_text'))
        if session_id:
            # Collect all skills
            all_skills = []
            all_skills.extend(structured_data.get('languages', []))
            all_skills.extend(structured_data.get('skills', []))
            all_skills.extend(structured_data.get('tools', []))
            
            complete_readme_session(session_id, readme_content, structured_data, all_skills)
            
            # Store session_id for rating
            context.user_data['session_id'] = session_id
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add README.md
            zip_file.writestr("README.md", readme_content.encode('utf-8'))
            
            # Load snake.yml workflow from template
            template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                         'resources', 'templates', 'snake.yml')
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    snake_workflow = f.read()
            except Exception as e:
                logger.error(f"Error loading snake template: {e}")
                snake_workflow = ""
            
            if snake_workflow:
                zip_file.writestr(".github/workflows/snake.yml", snake_workflow.encode('utf-8'))
        
        zip_buffer.seek(0)
        
        # Create filename using github username 
        user_name = user.get_data('github')
        filename = f"{user_name}.zip"
        
        # Send ZIP file - handle both callback query and regular message
        message_target = update.callback_query.message if hasattr(update, 'callback_query') and update.callback_query else update.message
        
        # Get user language preference
        user_language_code = conversation_manager.get_user_language(user_id)
        user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
        
        # Localized caption
        caption = language_manager.get_text("zip_caption", user_language, filename=filename, username=user.get_data('github'))
        
        # Localized buttons
        deploy_text = language_manager.get_text("auto_deploy_button", user_language)
        rating_text = language_manager.get_text("rate_bot_button", user_language)
        
        keyboard = [
            [InlineKeyboardButton(deploy_text, callback_data="deploy_github")],
            [InlineKeyboardButton(rating_text, callback_data="show_rating")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await message_target.reply_document(
            document=InputFile(zip_buffer, filename=filename),
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        logger.info(f"Successfully sent ZIP file to user {user_id}")
        
    except Exception as e:
        logger.error(f"Error generating ZIP file: {e}")
        # Handle error for both callback query and regular message
        message_target = update.callback_query.message if hasattr(update, 'callback_query') and update.callback_query else update.message
        await message_target.reply_text(
            "❌ An error occurred while generating your ZIP file. "
            "Please try again or contact support."
        )