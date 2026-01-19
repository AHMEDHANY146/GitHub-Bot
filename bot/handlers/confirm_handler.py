from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os
import tempfile
import zipfile
from io import BytesIO
from bot.states import BotState, conversation_manager
from utils.logger import Logger
from bot.handlers import voice_handler


logger = Logger.get_logger(__name__)


async def show_confirmation(update: Update, user_id: int):
    """Show confirmation with extracted information"""
    user = conversation_manager.get_user(user_id)
    structured_data = user.get_data('structured_data', {})
    
    # Format extracted information for display
    confirmation_text = format_confirmation_text(structured_data, user)
    
    # Create inline keyboard for confirmation
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve & Generate", callback_data="approve_readme"),
            InlineKeyboardButton("✏️ Edit Skills", callback_data="edit_skills")
        ],
        [
            InlineKeyboardButton("🔄 Regenerate", callback_data="regenerate_readme"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_readme")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(confirmation_text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(confirmation_text, reply_markup=reply_markup)
    
    logger.info(f"Showing confirmation for user {user_id}")


def format_confirmation_text(structured_data: dict, user) -> str:
    """Format the confirmation text with extracted information"""
    name = structured_data.get('name', 'Your Name')
    summary = structured_data.get('summary', 'No summary available')
    skills = structured_data.get('skills', [])
    tools = structured_data.get('tools', [])
    languages = structured_data.get('languages', [])
    
    # Get user's contact info
    github = user.get_data('github')
    linkedin = user.get_data('linkedin')
    portfolio = user.get_data('portfolio')
    email = user.get_data('email')
    
    confirmation = f"""📋 Review Your Information

Name: {name}

About Me:
{summary}

Skills ({len(skills)}):
{', '.join(skills[:10])}{'...' if len(skills) > 10 else ''}

Tools ({len(tools)}):
{', '.join(tools[:10])}{'...' if len(tools) > 10 else ''}

Languages ({len(languages)}):
{', '.join(languages[:10])}{'...' if len(languages) > 10 else ''}"""

    if github or linkedin or portfolio or email:
        confirmation += "\n\nContact Information:\n"
        if github:
            confirmation += f"• GitHub: {github}\n"
        if linkedin:
            confirmation += f"• LinkedIn: [Profile]({linkedin})\n"
        if portfolio:
            confirmation += f"• Portfolio: [Website]({portfolio})\n"
        if email:
            confirmation += f"• Email: {email}\n"
    
    confirmation += "\n\nIs this information correct? Choose an option below:"
    
    return confirmation


async def approve_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle approve README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Update state to completed
    conversation_manager.update_user_state(user_id, BotState.COMPLETED)
    
    # Generate and send ZIP file
    await generate_and_send_zip(update, user_id)
    
    logger.info(f"User {user_id} approved README generation")


async def edit_skills_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit skills callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Move back to text input for editing
    conversation_manager.update_user_state(user_id, BotState.WAITING_TEXT)
    
    edit_text = """
✏️ Edit Your Information

Please send me a corrected version of your experience. You can:

🎤 Send a new voice message, or
📝 Type a text description

Focus on any skills, tools, or languages I might have missed.
"""
    
    await query.edit_message_text(edit_text)
    logger.info(f"User {user_id} chose to edit skills")


async def regenerate_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regenerate README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Move back to processing
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    await query.edit_message_text("🔄 Regenerating your README...")
    
    # Re-process the data
    from bot.handlers.voice_handler import process_user_data
    await process_user_data(update, user_id)
    
    logger.info(f"User {user_id} chose to regenerate README")


async def cancel_readme_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel README callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Clear user data
    conversation_manager.clear_user(user_id)
    
    cancel_text = """
❌ README Generation Cancelled

Your session has been cleared. 

If you'd like to try again, just send /start to begin a new conversation!
"""
    
    await query.edit_message_text(cancel_text)
    logger.info(f"User {user_id} cancelled README generation")


async def generate_and_send_zip(update: Update, user_id: int):
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
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add README.md
            zip_file.writestr("README.md", readme_content.encode('utf-8'))
            
            # Add instructions file
            instructions = generate_instructions(structured_data, user)
            zip_file.writestr("INSTRUCTIONS.md", instructions.encode('utf-8'))
        
        zip_buffer.seek(0)
        
        # Create filename using github username 
        name = user.get_data('github')
        filename = f"{name}_README.zip"
        
        # Send ZIP file - handle both callback query and regular message
        message_target = update.callback_query.message if hasattr(update, 'callback_query') and update.callback_query else update.message
        
        await message_target.reply_document(
            document=InputFile(zip_buffer, filename=filename),
            caption=f"🎉 Your README is ready!\n\n"
                   f"📁 `{filename}` contains:\n"
                   f"• README.md - Your professional profile\n"
                   f"• INSTRUCTIONS.md - Setup guide\n\n"
                   f"📋 Next Steps:\n"
                   f"1. Extract the ZIP file\n"
                   f"2. Customize the README if needed\n"
                   f"3. Add it to your GitHub repository\n"
                   f"4. Update the contact links\n\n"
                   f"⭐ Don't forget to star this bot if it helped you!",
            parse_mode='Markdown'
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


def generate_instructions(structured_data: dict, user) -> str:
    """Generate instructions file for the ZIP"""
    name = structured_data.get('name', 'Your Name')
    github = user.get_data('github')
    linkedin = user.get_data('linkedin')
    portfolio = user.get_data('portfolio')
    email = user.get_data('email')
    
    instructions = f"""# README Setup Instructions

## 🎉 Your README is ready!

This README.md file has been generated based on your profile information. Here's how to set it up:

## 📋 Customization Required

### 1. Update Contact Information

Edit the "Connect With Me" section in README.md:

```markdown
## 🤝 Connect With Me

[![GitHub](https://img.shields.io/badge/GitHub-{github or 'yourusername'}-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/{github or 'yourusername'}){'[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](' + linkedin + ')' if linkedin else ''}{'[![Email](https://img.shields.io/badge/Email-Contact%20Me-red?style=for-the-badge&logo=gmail)](mailto:' + email + ')' if email else ''}{'[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-FF5722?style=for-the-badge&logo=todoist&logoColor=white)](' + portfolio + ')' if portfolio else ''}
```

### 2. Add Profile Badges (Optional)

Add these badges at the top of your README for more visibility:

```markdown
[![Profile Views](https://komarev.com/ghpvc/?username={github or 'yourusername'}&label=Profile%20views&color=0e75b6&style=flat)](https://github.com/{github or 'yourusername'})
[![GitHub Followers](https://img.shields.io/github/followers/{github or 'yourusername'}?style=social)](https://github.com/{github or 'yourusername'})
```

### 3. Add GitHub Stats (Optional)

If you want to include GitHub statistics, add this section:

```markdown
## 📊 GitHub Stats

![GitHub Stats](https://github-readme-stats.vercel.app/api?username={github or 'yourusername'}&show_icons=true&theme=radical)
![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={github or 'yourusername'}&layout=compact&theme=radical)
```

## 🚀 How to Use

1. **Copy** the README.md file to your GitHub repository root
2. **Edit** the contact links with your actual information
3. **Commit** and push to your repository
4. **View** your beautiful new README on GitHub!

## 💡 Tips

- The Devicon icons will automatically load from CDN
- You can customize colors, emojis, and sections as needed
- Consider adding project examples or achievements
- Keep your README updated with new skills and experiences

## 📞 Need Help?

If you need assistance with customization or have questions:
- Check GitHub's README documentation
- Look at other developers' READMEs for inspiration
- Use GitHub Markdown preview to test changes

---

Generated by GitHub README Bot 🤖
Generated on: {user.get_data('generated_date', 'Today')}
"""
    
    return instructions