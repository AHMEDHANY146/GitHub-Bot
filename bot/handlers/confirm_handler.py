from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes
import os
import tempfile
import zipfile
from io import BytesIO
from bot.states import BotState, conversation_manager
from utils.language import language_manager
from utils.logger import Logger
from bot.handlers import voice_handler
from bot.handlers.rating_handler import show_rating_prompt
from utils.language import Language
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
    # Get bilingual button texts (Masri uses Arabic text for buttons mostly)
    is_ar_or_masri = user_language == Language.ARABIC or user_language == Language.EGYPTIAN
    
    edit_contact_text = "✏️ تعديل الاسم/الروابط" if is_ar_or_masri else "✏️ Edit Name/Links"
    add_tech_text = "🔧 إضافة تقنيات" if is_ar_or_masri else "🔧 Add Tech Stack"
    
    keyboard = [
        [
            InlineKeyboardButton(language_manager.get_text("approve_button", user_language), callback_data="approve_readme"),
            InlineKeyboardButton(language_manager.get_text("edit_button", user_language), callback_data="edit_skills")
        ],
        [
            InlineKeyboardButton(edit_contact_text, callback_data="edit_contact"),
            InlineKeyboardButton(add_tech_text, callback_data="add_tech_stack")
        ],
        [
            InlineKeyboardButton(language_manager.get_text("regenerate_button", user_language), callback_data="regenerate_readme"),
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
    """Format the confirmation text with extracted information - comprehensive version"""
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
    
    # Check if Arabic or Masri
    is_arabic = user_language == Language.ARABIC or user_language == Language.EGYPTIAN
    
    # Build comprehensive confirmation text based on language
    if is_arabic:
        confirmation = "📋 **مراجعة المعلومات المستخرجة**\n"
        confirmation += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Personal Info Section
        confirmation += "👤 **المعلومات الشخصية:**\n"
        confirmation += f"• **الاسم:** {name}\n"
        if github:
            confirmation += f"• **GitHub:** {github}\n"
        if linkedin:
            confirmation += f"• **LinkedIn:** [الملف الشخصي]({linkedin})\n"
        if portfolio:
            confirmation += f"• **الموقع:** [زيارة]({portfolio})\n"
        if email:
            confirmation += f"• **البريد:** {email}\n"
        
        # Summary Section
        if summary:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += "📝 **نبذة عني:**\n"
            confirmation += f"{summary}\n"
        
        # Programming Languages
        if languages:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"💻 **لغات البرمجة ({len(languages)}):**\n"
            confirmation += format_skill_list_improved(languages, is_arabic)
        
        # Skills & Technologies  
        if skills:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"🛠️ **المهارات والتقنيات ({len(skills)}):**\n"
            confirmation += format_skill_list_improved(skills, is_arabic)
        
        # Tools
        if tools:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"🔧 **الأدوات والمنصات ({len(tools)}):**\n"
            confirmation += format_skill_list_improved(tools, is_arabic)
        
        # Dynamic sections
        confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        confirmation += "🎯 **معلومات إضافية:**\n"
        if currently_working_on:
            confirmation += f"• 🚀 **أعمل حالياً على:** {currently_working_on}\n"
        if currently_learning:
            confirmation += f"• 📚 **أتعلم حالياً:** {currently_learning}\n"
        if open_to:
            confirmation += f"• 🤝 **مفتوح لـ:** {open_to}\n"
        if fun_fact:
            confirmation += f"• ⚡ **حقيقة ممتعة:** {fun_fact}\n"
        
        confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        # Using specific dialect prompt if available, otherwise generic Arabic
        prompt_text = language_manager.get_text("confirmation_prompt", user_language)
        confirmation += f"✅ {prompt_text}"
        
    else:
        confirmation = "📋 **Review Extracted Information**\n"
        confirmation += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Personal Info Section
        confirmation += "👤 **Personal Information:**\n"
        confirmation += f"• **Name:** {name}\n"
        if github:
            confirmation += f"• **GitHub:** {github}\n"
        if linkedin:
            confirmation += f"• **LinkedIn:** [Profile]({linkedin})\n"
        if portfolio:
            confirmation += f"• **Portfolio:** [Visit]({portfolio})\n"
        if email:
            confirmation += f"• **Email:** {email}\n"
        
        # Summary Section
        if summary:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += "📝 **About Me:**\n"
            confirmation += f"{summary}\n"
        
        # Programming Languages
        if languages:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"💻 **Programming Languages ({len(languages)}):**\n"
            confirmation += format_skill_list_improved(languages, is_arabic)
        
        # Skills & Technologies  
        if skills:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"🛠️ **Skills & Technologies ({len(skills)}):**\n"
            confirmation += format_skill_list_improved(skills, is_arabic)
        
        # Tools
        if tools:
            confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
            confirmation += f"🔧 **Tools & Platforms ({len(tools)}):**\n"
            confirmation += format_skill_list_improved(tools, is_arabic)
        
        # Dynamic sections
        confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        confirmation += "🎯 **Additional Information:**\n"
        if currently_working_on:
            confirmation += f"• 🚀 **Currently Working On:** {currently_working_on}\n"
        if currently_learning:
            confirmation += f"• 📚 **Currently Learning:** {currently_learning}\n"
        if open_to:
            confirmation += f"• 🤝 **Open To:** {open_to}\n"
        if fun_fact:
            confirmation += f"• ⚡ **Fun Fact:** {fun_fact}\n"
        
        confirmation += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        confirmation += "✅ Is this information correct? Choose an option:"
    
    return confirmation


def format_skill_list_improved(skills: list, is_arabic: bool = False) -> str:
    """Format a list of skills for display - improved version"""
    if not skills:
        return "لا يوجد" if is_arabic else "None"
    
    # Format skills in a clean grid-like display
    formatted_skills = [skill.title() for skill in skills]
    
    # Show all skills, formatted nicely
    if len(formatted_skills) <= 15:
        # Show in rows of 3-4 skills
        rows = []
        for i in range(0, len(formatted_skills), 4):
            row_skills = formatted_skills[i:i+4]
            rows.append("  " + " • ".join(row_skills))
        return "\n".join(rows)
    else:
        # Show first 12 with indicator
        shown = formatted_skills[:12]
        remaining = len(formatted_skills) - 12
        rows = []
        for i in range(0, len(shown), 4):
            row_skills = shown[i:i+4]
            rows.append("  " + " • ".join(row_skills))
        
        more_text = f"و {remaining} مهارة أخرى..." if is_arabic else f"... and {remaining} more"
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
    """Handle edit skills callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Move back to text input for editing
    conversation_manager.update_user_state(user_id, BotState.WAITING_TEXT)
    
    edit_text = language_manager.get_text("edit_prompt", user_language)
    
    await query.edit_message_text(edit_text)
    logger.info(f"User {user_id} chose to edit skills")


async def edit_contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle edit contact information callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Move to contact editing state
    conversation_manager.update_user_state(user_id, BotState.WAITING_CONTACT)
    
    contact_edit_text = """✏️ **Edit Contact Information**

Please send your updated information in this format:

**Name:** Your Full Name
**GitHub:** github-username  
**LinkedIn:** https://linkedin.com/in/your-profile
**Portfolio:** https://your-website.com
**Email:** your.email@example.com

You can send only the fields you want to update. For example:
```
Name: John Doe
GitHub: johndoe
```

Send /cancel to go back."""
    
    await query.edit_message_text(contact_edit_text)
    logger.info(f"User {user_id} chose to edit contact information")


async def add_tech_stack_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle add tech stack callback"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Move to tech stack adding state
    conversation_manager.update_user_state(user_id, BotState.WAITING_TECH_STACK)
    
    tech_stack_text = """🔧 **Add Tech Stack Items**

Please send additional technologies, tools, or skills you want to add:

**Examples:**
- Programming languages: python, javascript, typescript, go, rust
- Frameworks: react, vue, angular, django, flask
- Tools: docker, kubernetes, git, aws, azure
- Databases: mysql, postgresql, mongodb, redis
- Other: power bi, tableau, jupyter

You can send them as a comma-separated list:
```
react, typescript, docker, aws, postgresql
```

Send /cancel to go back."""
    
    await query.edit_message_text(tech_stack_text)
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
            
            # Add snake.yml workflow file
            snake_workflow = """name: Generate snake animation

on:
  schedule:
    - cron: "0 */12 * * *"
  workflow_dispatch:
  push:
    branches:
      - main

jobs:
  generate:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Generate snake animation
        uses: Platane/snk@v3
        with:
          github_user_name: ${{ github.repository_owner }}
          outputs: |
            dist/snake.svg
            dist/snake-dark.svg?palette=github-dark
            dist/snake.gif?color_snake=orange&color_dots=#bfd6f6,#8dbdff,#64a1f4,#4b91f1,#3c7dd9
          github_token: ${{ secrets.GITHUB_TOKEN }}

      - name: Deploy to output branch
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_branch: output
          publish_dir: ./dist
          force_orphan: true"""
            
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
        
        # Bilingual caption with support link
        if user_language == Language.ARABIC or user_language == Language.EGYPTIAN:
            caption = f"""🎉 **ملفك جاهز!** `{filename}`

👇 **خطوات التثبيت اليدوي:**

1️⃣ **إنشاء المستودع (هام جدًا):**
• سمِّه بنفس **اسم المستخدم** ({user.get_data('github')}).
• اجعله **Public**.

2️⃣ **رفع الملفات:**
• فك الضغط وارفع الكل (خاصة مجلد `.github`).
• `README.md` في الواجهة.

3️⃣ **تفعيل السنيك (Snake 🐍):**
• Settings > Actions > General
• اختر **Read and write permissions** واحفظ.

4️⃣ **التشغيل:**
• Actions > Generate snake animation > Run workflow 🚀.

⚡ **ريح نفسك واستخدم "النشر التلقائي" 👇**

💝 **دعم المطور:**
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH"""
        else:
            caption = f"""🎉 **Profile Ready!** `{filename}`

👇 **Manual Setup Guide:**

1️⃣ **Create Repo (Critical):**
• Name it **SAME as Username** ({user.get_data('github')}).
• Set to **Public**.

2️⃣ **Upload Files:**
• Extract & upload all (keep `.github` folder).
• `README.md` at root.

3️⃣ **Enable Snake 🐍:**
• Settings > Actions > General
• Select **Read and write permissions** & Save.

4️⃣ **Run:**
• Actions > Generate snake animation > Run workflow 🚀.

⚡ **Save time using "Auto-Deploy" below 👇**

💝 **Support Developer:**
https://ipn.eg/S/ahmedhanycs/instapay/5Ni1NH"""
        
        # Create keyboard with Auto-Deploy option
        deploy_text = "🚀 النشر التلقائي على GitHub" if (user_language == Language.ARABIC or user_language == Language.EGYPTIAN) else "🚀 Auto-Deploy to GitHub"
        rating_text = "⭐ تقييم البوت" if (user_language == Language.ARABIC or user_language == Language.EGYPTIAN) else "⭐ Rate Bot"
        
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
        
        # Show rating prompt after successful delivery DO NOT show it immediately now, let user choose
        # await show_rating_prompt(update, context)
        
    except Exception as e:
        logger.error(f"Error generating ZIP file: {e}")
        # Handle error for both callback query and regular message
        message_target = update.callback_query.message if hasattr(update, 'callback_query') and update.callback_query else update.message
        await message_target.reply_text(
            "❌ An error occurred while generating your ZIP file. "
            "Please try again or contact support."
        )