import os
import sys

# Add project root to Python path (works from any directory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from telegram.ext import Application
from dotenv import load_dotenv
from bot.router import setup_handlers, setup_error_handlers
from utils.logger import Logger
from helpers.config import get_settings


settings = get_settings()


# Load environment variables
load_dotenv()

# Configure logging
logger = Logger.get_logger(__name__)


def main():
    # Validate required environment variables
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        logger.error("Please set up your .env file with the required bot token.")
        return
    
    # Check for at least one LLM provider
    gemini_key = settings.GEMINI_API_KEY
    cohere_key = settings.COHERE_API_KEY
    
    if not gemini_key and not cohere_key:
        logger.error("No LLM API keys found! Please set either GEMINI_API_KEY or COHERE_API_KEY.")
        return
    
    # Create the Application
    logger.info("Starting GitHub README Bot...")
    application = Application.builder().token(token).build()
    
    # Setup handlers
    setup_handlers(application)
    setup_error_handlers(application)
    
    # Log startup information
    logger.info("Bot configuration complete!")
    logger.info(f"Using Gemini: {'Yes' if gemini_key else 'No'}")
    logger.info(f"Using Cohere: {'Yes' if cohere_key else 'No'}")
    logger.info(f"Using Groq: {'Yes' if settings.GROQ_API_KEY else 'No'}")
    
    # Create output directories
    outputs_dir = os.path.join(project_root, "outputs")
    os.makedirs(os.path.join(outputs_dir, "readmes"), exist_ok=True)
    os.makedirs(os.path.join(outputs_dir, "zips"), exist_ok=True)
    os.makedirs(os.path.join(project_root, "logs"), exist_ok=True)
    
    # Initialize database
    try:
        # Supabase client is lazy initialized on first use, but we can check connection here if needed
        from services.DB.client import get_supabase
        # get_supabase() # This would check connection if we want to fail early, but config might be missing.
        # Let's just log.
        logger.info("Database (Supabase) integration enabled")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        
    # Setup scheduled jobs (Daily stats for developer)
    try:
        from bot.job_scheduler import setup_scheduler
        setup_scheduler(application)
    except Exception as e:
        logger.error(f"Failed to setup job scheduler: {e}")
    
    # Start the bot
    logger.info("Bot is starting...")
    
    # Run polling in a loop to handle temporary connection issues
    while True:
        try:
            application.run_polling(
                allowed_updates=["message", "callback_query", "chat_member"],
                drop_pending_updates=True
            )
            # If run_polling returns, it means the bot was stopped cleanly
            break
        except Exception as e:
            logger.error(f"Polling loop crashed: {e}")
            logger.info("Restarting polling in 5 seconds...")
            import time
            time.sleep(5)
            # Continue loop to restart


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        # Don't exit on crash, try to restart main if possible or just log critical state
        # But usually main() loop handles network errors. 
        # For critical startup errors, we exit.
        sys.exit(1)