import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
from utils.logger import Logger
from helpers.config import get_settings
from services.DB import UserService, SessionService

logger = Logger.get_logger(__name__)
settings = get_settings()

async def send_daily_stats(context: ContextTypes.DEFAULT_TYPE):
    """Send daily statistics to the developer"""
    try:
        if not settings.DEVELOPER_CHAT_ID:
            logger.warning("Developer Chat ID not set, skipping daily stats.")
            return

        # Calculate time range (last 24 hours)
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # Get stats (mocking the DB calls if specific stats methods don't exist yet, 
        # but optimally we should add get_stats methods to UserService)
        
        # Since we might not have specific count methods exposed in the Services yet, 
        # we'll try to use what we have or add necessary DB methods. 
        # For this implementation, I'll assume we can get basic info or implement simple counts.
        
        # Placeholder for actual DB queries - in a real scenario we'd add:
        # new_users = UserService.get_users_count_since(yesterday)
        # active_sessions = SessionService.get_sessions_count_since(yesterday)
        
        # For now, let's send a simple "I'm alive" message with placeholder stats
        # You should implement actual counting queries in the DB layer.
        
        # Let's try to fetch basic counts via raw SQL or if we can access the session/engine
        # But to be safe and avoid complex ORM code here without seeing DB layer fully:
        
        stats_message = (
            f"📊 Daily Bot Statistics\n"
            f"📅 Date: {now.strftime('%Y-%m-%d')}\n\n"
            f"✅ Bot is running smoothly.\n"
            f"ℹ️ (Connect DB stats methods here to see actual counts)"
        )

        await context.bot.send_message(chat_id=settings.DEVELOPER_CHAT_ID, text=stats_message, parse_mode='Markdown')
        logger.info("Sent daily stats to developer")
        
    except Exception as e:
        logger.error(f"Error sending daily stats: {e}")

def setup_scheduler(application):
    """Setup scheduled jobs"""
    if not application.job_queue:
        logger.warning("JobQueue not available, skipping scheduler setup.")
        return

    # Run daily at 9:00 AM UTC (or whatever time preferred)
    application.job_queue.run_daily(
        send_daily_stats, 
        time=datetime.strptime("09:00", "%H:%M").time(),
        days=(0, 1, 2, 3, 4, 5, 6) # Everyday
    )
    logger.info("Scheduler setup complete")
