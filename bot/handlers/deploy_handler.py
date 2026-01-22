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

logger = Logger.get_logger(__name__)


async def request_github_token_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle request to deploy to GitHub"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Update state
    conversation_manager.update_user_state(user_id, BotState.WAITING_GITHUB_TOKEN)
    
    # Message explaining why we need the token and how to get it
    text = language_manager.get_text("deploy_intro_text", user_language)
    
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
    
    # Status message
    status_msg = await update.message.reply_text(
        language_manager.get_text("validating_token", user_language)
    )
    
    # Initialize GitHub API
    github = GitHubAPI(token)
    
    # Validate token
    username = await github.validate_token()
    
    if not username:
        await status_msg.edit_text(
            language_manager.get_text("invalid_token", user_language)
        )
        return

    # Check against provided username (optional security check)
    stored_username = conversation_manager.get_user_data(user_id, 'github')
    if stored_username and stored_username.lower() != username.lower():
        warning_text = language_manager.get_text(
            "token_warning", 
            user_language, 
            username=username, 
            stored_username=stored_username
        )
        await status_msg.edit_text(warning_text)
        await asyncio.sleep(2)
    
    # Start deployment process
    verified_text = language_manager.get_text("token_verified", user_language, username=username)
    await status_msg.edit_text(verified_text)
    
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
            language_manager.get_text("uploading_readme", user_language)
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
            language_manager.get_text("setting_up_snake", user_language)
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
        
        success_text = language_manager.get_text("deploy_success", user_language, repo_url=repo_url)

        await status_msg.edit_text(success_text, parse_mode='Markdown')
        
        # Mark state as completed
        conversation_manager.update_user_state(user_id, BotState.COMPLETED)
        
        # Log success
        logger.info(f"Successfully auto-deployed for user {user_id} to {username}/{repo_name}")
        
    except Exception as e:
        logger.error(f"Deployment error for {user_id}: {e}")
        error_msg = language_manager.get_text("deploy_error", user_language, error=str(e))
        await status_msg.edit_text(error_msg)
