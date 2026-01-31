"""
Skill Selection Handler
Handles interactive skill selection with toggle buttons
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.states import BotState, conversation_manager
from utils.language import language_manager, Language
from utils.logger import Logger
from resources.common_skills import get_popular_skills

logger = Logger.get_logger(__name__)

# Number of skills to show per page
SKILLS_PER_PAGE = 15


def get_user_selected_skills(user_id: int) -> set:
    """Get currently selected skills for user"""
    user = conversation_manager.get_user(user_id)
    structured_data = user.get_data('structured_data', {})
    
    # Combine all skills from different categories
    all_skills = set()
    for key in ['skills', 'tools', 'languages']:
        skills = structured_data.get(key, [])
        if skills:
            all_skills.update([s.lower() for s in skills])
    
    return all_skills


def build_skill_keyboard(user_id: int, page: int = 0) -> tuple:
    """Build keyboard with skill toggle buttons"""
    user_language = conversation_manager.get_user_language(user_id)
    selected_skills = get_user_selected_skills(user_id)
    
    # Get popular skills
    all_popular = get_popular_skills(50)
    
    # Add AI-extracted skills that might not be in popular list
    for skill in selected_skills:
        if skill not in all_popular:
            all_popular.append(skill)
    
    # Pagination
    total_pages = (len(all_popular) + SKILLS_PER_PAGE - 1) // SKILLS_PER_PAGE
    start_idx = page * SKILLS_PER_PAGE
    end_idx = min(start_idx + SKILLS_PER_PAGE, len(all_popular))
    page_skills = all_popular[start_idx:end_idx]
    
    # Build skill buttons (3 per row)
    keyboard = []
    row = []
    for skill in page_skills:
        is_selected = skill.lower() in selected_skills
        icon = "✅" if is_selected else "⬜"
        display_name = skill.title() if len(skill) <= 12 else skill[:10].title() + ".."
        button = InlineKeyboardButton(
            f"{icon} {display_name}",
            callback_data=f"skill_toggle_{skill}"
        )
        row.append(button)
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    if row:  # Add remaining buttons
        keyboard.append(row)
    
    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️", callback_data=f"skill_page_{page-1}"))
    nav_row.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="skill_noop"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("➡️", callback_data=f"skill_page_{page+1}"))
    keyboard.append(nav_row)
    
    # Done button
    done_text = language_manager.get_text("done_button", user_language, default="✅ Done")
    keyboard.append([InlineKeyboardButton(done_text, callback_data="skill_done")])
    
    return InlineKeyboardMarkup(keyboard), len(selected_skills)


async def show_skill_selection(update: Update, user_id: int, page: int = 0):
    """Show skill selection screen"""
    user_language = conversation_manager.get_user_language(user_id)
    
    # Update state
    conversation_manager.update_user_state(user_id, BotState.WAITING_SKILL_SELECTION)
    
    # Build keyboard
    keyboard, skill_count = build_skill_keyboard(user_id, page)
    
    # Build message
    text = language_manager.get_text(
        "skill_selection_prompt", 
        user_language,
        default=f"""🛠️ **Skill Selection**

Selected: {skill_count} skills

Tap to toggle skills on/off:
✅ = Selected (will be in your README)
⬜ = Not selected

After editing, tap "Done" to regenerate your README."""
    )
    
    if hasattr(update, 'callback_query') and update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
        except Exception:
            await update.callback_query.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
    
    logger.info(f"Showing skill selection for user {user_id}")


async def handle_skill_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skill toggle button press"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    skill = query.data.replace("skill_toggle_", "")
    
    # Get current skills
    user = conversation_manager.get_user(user_id)
    structured_data = user.get_data('structured_data', {})
    
    # Get all skills as a combined list
    all_skills = []
    for key in ['skills', 'tools', 'languages']:
        all_skills.extend(structured_data.get(key, []))
    
    # Toggle skill
    skill_lower = skill.lower()
    all_skills_lower = [s.lower() for s in all_skills]
    
    if skill_lower in all_skills_lower:
        # Remove skill
        for key in ['skills', 'tools', 'languages']:
            current = structured_data.get(key, [])
            structured_data[key] = [s for s in current if s.lower() != skill_lower]
    else:
        # Add skill to 'skills' category
        if 'skills' not in structured_data:
            structured_data['skills'] = []
        structured_data['skills'].append(skill)
    
    # Save updated data
    user.add_data('structured_data', structured_data)
    
    # Get current page from context or default to 0
    current_page = context.user_data.get('skill_page', 0)
    
    # Refresh keyboard
    await show_skill_selection(update, user_id, current_page)
    
    logger.info(f"User {user_id} toggled skill: {skill}")


async def handle_skill_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle skill page navigation"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    page = int(query.data.replace("skill_page_", ""))
    
    # Store current page
    context.user_data['skill_page'] = page
    
    # Show new page
    await show_skill_selection(update, user_id, page)


async def handle_skill_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle done button - regenerate README with selected skills (without LLM re-extraction)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language = conversation_manager.get_user_language(user_id)
    
    # Update state to processing
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    # Show processing message
    await query.edit_message_text(
        language_manager.get_text("regenerating", user_language, default="🔄 Regenerating your README with updated skills...")
    )
    
    # Regenerate README with existing structured_data (don't re-extract from LLM)
    try:
        user = conversation_manager.get_user(user_id)
        structured_data = user.get_data('structured_data', {})
        
        # Import MarkdownGenerator
        from utils.markdown import MarkdownGenerator
        from bot.handlers.confirm_handler import show_confirmation
        
        # Generate new README with updated skills
        markdown_generator = MarkdownGenerator()
        readme_content = markdown_generator.generate_readme(structured_data)
        
        # Save updated README
        user.add_data('readme_content', readme_content)
        
        # Move to confirmation state
        conversation_manager.update_user_state(user_id, BotState.CONFIRMATION)
        
        # Show confirmation
        await show_confirmation(update, user_id)
        
        logger.info(f"User {user_id} completed skill selection - README regenerated")
        
    except Exception as e:
        logger.error(f"Error regenerating README after skill selection: {e}")
        await query.message.reply_text(
            language_manager.get_text("processing_error", user_language, default="❌ An error occurred. Please try again.")
        )


async def handle_skill_noop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle no-op button (page indicator)"""
    query = update.callback_query
    await query.answer()
