from telegram import Update
from telegram.ext import ContextTypes
import os
import tempfile
from services.stt.STTProviderFactory import STTProviderFactory
from services.llm.LLMProviderFactory import LLMProviderFactory
from services.prompt_engine import PromptEngine
from utils.markdown import MarkdownGenerator
from utils.validators import Validators
from utils.logger import Logger
from utils.language import language_manager, Language
from bot.states import BotState, conversation_manager
from bot.handlers.confirm_handler import show_confirmation


logger = Logger.get_logger(__name__)


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages and process them"""
    user_id = update.effective_user.id
    user = conversation_manager.get_user(user_id)
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    # Only handle voice messages when waiting for experience
    if user.state not in [BotState.WAITING_VOICE, BotState.WAITING_TEXT, BotState.WAITING_EDIT_TEXT]:
        await update.message.reply_text(language_manager.get_text("please_complete_previous_steps", user_language, default="Please complete the previous steps first. Use /start to begin."))
        return
    
    try:
        # Send processing message
        await update.message.reply_text(language_manager.get_text("processing_voice_message", user_language, default="🎤 Processing your voice message..."))
        
        # Get voice file
        voice_file = await update.message.voice.get_file()
        
        # Download voice file to temporary location
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
            await voice_file.download_to_drive(temp_file.name)
            temp_file_path = temp_file.name
        
        # Add to cleanup list
        user.add_temp_file(temp_file_path)
        
        try:
            # Transcribe audio
            transcribed_text = await transcribe_audio(temp_file_path)
            
            if transcribed_text:
                # Save transcribed text
                conversation_manager.add_user_data(user_id, 'experience_text', transcribed_text)
                
                # Start processing
                await start_processing(update, user_id)
            else:
                await update.message.reply_text(
                    language_manager.get_text("voice_transcription_failed", user_language, default="""❌ Sorry, I couldn't understand your voice message. 
This could be due to:
• Poor audio quality
• Background noise
• Unsupported audio format

Please try again speaking clearly or type your experience instead.""")
                )
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
                user.temp_files.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")
                
    except Exception as e:
        logger.error(f"Error in voice_handler: {e}")
        await update.message.reply_text(language_manager.get_text("voice_processing_error", user_language, default="❌ An error occurred while processing your voice message"))


async def transcribe_audio(audio_file_path: str) -> str:
    """Transcribe audio file using STT provider"""
    try:
        # Get STT provider
        stt_provider = STTProviderFactory.get_default_provider()
        
        # Transcribe audio
        transcribed_text = stt_provider.transcribe_audio(audio_file_path)
        
        if transcribed_text and transcribed_text.strip():
            logger.info(f"Successfully transcribed audio: {len(transcribed_text)} characters")
            return transcribed_text.strip()
        else:
            logger.error("STT provider returned empty transcription")
            return None
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return None


async def process_user_data(update: Update, user_id: int):
    """Process collected user data and generate README"""
    try:
        user = conversation_manager.get_user(user_id)
        user_language_code = conversation_manager.get_user_language(user_id)
        user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
        
        # Get experience text
        experience_text = user.get_data('experience_text')
        if not experience_text:
            await update.message.reply_text(language_manager.get_text("no_experience_data", user_language, default="❌ No experience data found. Please try again."))
            return
        
        # Get LLM provider
        llm_provider = LLMProviderFactory.get_default_provider()
        
        # Extract structured data
        schema = PromptEngine.get_structured_data_schema()
        structured_data = llm_provider.extract_structured_data(experience_text, schema)
        
        if not structured_data:
            await update.message.reply_text(
                language_manager.get_text("structured_extraction_failed", user_language, default="❌ I couldn't extract structured information from your input. Please provide more details about your skills and experience.")
            )
            return
        
        # Add user's name to structured data
        user_name = user.get_data('name', 'Your Name')
        structured_data['name'] = user_name
        
        # Add contact information to structured data for badge generation
        github_username = user.get_data('github')
        if github_username:
            structured_data['github'] = github_username
        
        linkedin_url = user.get_data('linkedin')
        if linkedin_url:
            structured_data['linkedin'] = linkedin_url
            
        email = user.get_data('email')
        if email:
            structured_data['email'] = email
            
        portfolio = user.get_data('portfolio')
        if portfolio:
            structured_data['portfolio'] = portfolio
        
        # Validate and clean skills
        if 'skills' in structured_data:
            structured_data['skills'] = Validators.validate_skills(structured_data['skills'])
        
        if 'tools' in structured_data:
            structured_data['tools'] = Validators.validate_skills(structured_data['tools'])
        
        if 'languages' in structured_data:
            structured_data['languages'] = Validators.validate_skills(structured_data['languages'])
        
        # Save structured data
        user.add_data('structured_data', structured_data)
        
        # Generate README
        markdown_generator = MarkdownGenerator()
        readme_content = markdown_generator.generate_readme(structured_data)
        
        # Save README content
        user.add_data('readme_content', readme_content)
        
        # Move to confirmation state
        conversation_manager.update_user_state(user_id, BotState.CONFIRMATION)
        
        # Show confirmation
        await show_confirmation(update, user_id)
        
        logger.info(f"Successfully processed data for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing user data: {e}")
        await update.message.reply_text(
            language_manager.get_text("processing_error", user_language, default="❌ An error occurred while processing your information. Please try again or contact support.")
        )


async def start_processing(update: Update, user_id: int):
    """Start processing the collected information"""
    user_language_code = conversation_manager.get_user_language(user_id)
    user_language = language_manager.get_language_from_code(user_language_code) if user_language_code else Language.ENGLISH
    
    conversation_manager.update_user_state(user_id, BotState.PROCESSING)
    
    processing_text = language_manager.get_text("processing_information", user_language, default="""🔄 Processing your information

I'm analyzing your experience and extracting:
• Technical skills
• Programming languages  
• Tools and platforms
• Professional summary

This will take a few moments""")
    
    await update.message.reply_text(processing_text)
    logger.info(f"User {user_id} moved to processing state")
    
    # Trigger processing
    await process_user_data(update, user_id)









