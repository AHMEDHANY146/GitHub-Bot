"""
Deploy Handler
Handles automatic deployment to GitHub
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import asyncio
from bot.states import BotState, conversation_manager
from utils.language import language_manager, Language
from utils.logger import Logger
from services.github_api import GitHubAPI
from bot.db_helper import complete_readme_session

logger = Logger.get_logger(__name__)


async def request_github_token_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle request to deploy to GitHub"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    is_arabic = user_language == Language.ARABIC
    
    # Update state
    # Update state
    conversation_manager.update_user_state(user_id, BotState.WAITING_GITHUB_TOKEN)
    
    # Message explaining why we need the token and how to get it
    if is_arabic or user_language == Language.EGYPTIAN:
        text = """🚀 **النشر التلقائي على GitHub**

للقيام بذلك، نحتاج إلى **Personal Access Token** خاص بك مع الصلاحيات التالية:
1. `repo` (للتحكم بالمستودعات الخاصة/العامة)
2. `workflow` (لتفعيل الـ Actions)

**كيف تحصل عليه؟**
1. اذهب إلى GitHub Settings > Developer settings
2. اختر Personal access tokens > Tokens (classic)
3. انشأ Token جديد واختر الصلاحيات المطلوبة
4. انسخ الـ Token وأرسله هنا 👇

⚠️ **ملاحظة:** نحن لا نحفظ الـ Token، نستخدمه مرة واحدة فقط للنشر ثم ننساه تماماً للأمان.

أرسل الـ Token الآن أو أرسل /cancel للإلغاء."""
    else:
        text = """🚀 **Auto-Deploy to GitHub**

To do this, we need your **Personal Access Token** with these scopes:
1. `repo` (Full control of private repositories)
2. `workflow` (Update GitHub Action workflows)

**How to get it?**
1. Go to GitHub Settings > Developer settings
2. Select Personal access tokens > Tokens (classic)
3. Generate new token and select required scopes
4. Copy the token and send it here 👇

⚠️ **Note:** We DO NOT store your token. We use it once for deployment and then forget it immediately for security.

Send your Token now or /cancel to cancel."""
    
    # Use reply_text instead of edit_message_text because the previous message is a document (ZIP)
    await query.message.reply_text(text, parse_mode='Markdown')
    logger.info(f"User {user_id} requested GitHub auto-deployment")


async def handle_github_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the received GitHub token"""
    token = update.message.text.strip()
    user_id = update.effective_user.id
    
    # Check if this is a valid token format (basic check)
    if not token.startswith(('ghp_', 'github_pat_')) and len(token) < 10:
        # Not a strict check, let the API decide
        pass
        
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    is_arabic = user_language == Language.ARABIC or user_language == Language.EGYPTIAN
    
    # Status message
    status_msg = await update.message.reply_text(
        "⏳ جاري التحقق من الـ Token..." if is_arabic else "⏳ Validating Token..."
    )
    
    # Initialize GitHub API
    github = GitHubAPI(token)
    
    # Validate token
    username = await github.validate_token()
    
    if not username:
        await status_msg.edit_text(
            "❌ **Token غير صالح!**\nتأكد من نسخه بشكل صحيح وحاول مرة أخرى." if is_arabic
            else "❌ **Invalid Token!**\nPlease make sure you copied it correctly and try again."
        )
        return

    # Check against provided username (optional security check)
    stored_username = conversation_manager.get_user_data(user_id, 'github')
    if stored_username and stored_username.lower() != username.lower():
        await status_msg.edit_text(
            f"⚠️ **تنبيه:** الـ Token ينتمي للمستخدم `{username}` بينما أدخلت سابقاً `{stored_username}`.\nسأقوم بالنشر على حساب `{username}`." if is_arabic
            else f"⚠️ **Warning:** Token belongs to user `{username}` but you previously entered `{stored_username}`.\nI will deploy to `{username}` account."
        )
        await asyncio.sleep(2)
    
    # Start deployment process
    await status_msg.edit_text(
        f"✅ تم التحقق! مرحباً `{username}`\n🚀 جاري إنشاء المستودع ورفع الملفات..." if is_arabic
        else f"✅ Verified! Hello `{username}`\n🚀 Creating repository and uploading files..."
    )
    
    try:
        # 1. Get user data
        user = conversation_manager.get_user(user_id)
        readme_content = user.get_data('readme_content')
        
        # 2. Repo name (username/username for profile readme)
        repo_name = username 
        
        # 3. Check/Create Repo
        repo = await github.get_repo(username, repo_name)
        if not repo:
            success = await github.create_repo(repo_name, "My Professional Portfolio", private=False)
            if not success:
                raise Exception("Failed to create repository")
            await asyncio.sleep(1) # Wait for propagation
        
        # 4. Upload README.md
        await status_msg.edit_text(
            "📤 جاري رفع README.md..." if is_arabic else "📤 Uploading README.md..."
        )
        
        success = await github.update_file(
            username, repo_name, 
            "README.md", 
            readme_content, 
            "Update README.md via GitHub Bot"
        )
        if not success:
            raise Exception("Failed to upload README.md")
            
        # 5. Upload Snake Workflow
        await status_msg.edit_text(
            "🐍 جاري إعداد Snake Animation..." if is_arabic else "🐍 Setting up Snake Animation..."
        )
        
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
          
        success = await github.update_file(
            username, repo_name,
            ".github/workflows/snake.yml",
            snake_workflow,
            "Add Snake Animation Workflow"
        )
        
        # 6. Trigger Workflow
        if success:
            await github.trigger_workflow(username, repo_name, "snake.yml")
            
        # 7. Success!
        repo_url = f"https://github.com/{username}/{repo_name}"
        
        success_text = f"""🎉 **تم النشر بنجاح!**

🔗 رابط المستودع: {repo_url}

✅ تم رفع README.md
✅ تم إعداد Snake Animation
✅ تم تفعيل وتشغيل الـ Actions

قد يأخذ الـ Snake Animation بضع دقائق ليظهر (بعد انتهاء الـ GitHub Action).

شكراً لاستخدامك البوت!""" if is_arabic else f"""🎉 **Deployment Successful!**

🔗 Repo Link: {repo_url}

✅ README.md uploaded
✅ Snake Animation configured
✅ Actions enabled and triggered

The Snake Animation might take a few minutes to appear (after GitHub Action finishes).

Thank you for using the bot!"""

        await status_msg.edit_text(success_text, parse_mode='Markdown')
        
        # Mark state as completed
        conversation_manager.update_user_state(user_id, BotState.COMPLETED)
        
        # Log success
        logger.info(f"Successfully auto-deployed for user {user_id} to {username}/{repo_name}")
        
    except Exception as e:
        logger.error(f"Deployment error for {user_id}: {e}")
        await status_msg.edit_text(
            f"❌ **حدث خطأ أثناء النشر:**\n{str(e)}\n\nحاول مرة أخرى أو قم بالنشر يدوياً باستخدام ملف ZIP." if is_arabic
            else f"❌ **Deployment Error:**\n{str(e)}\n\nPlease try again or deploy manually using the ZIP file."
        )
