# GitHub README Bot - Complete Setup Guide

## 🚀 Overview

This advanced Telegram bot converts user voice messages or text into professional GitHub README.md files with AI-powered information extraction and Devicon icons.

## ✨ Features

- 🎤 **Voice-to-text processing** with Gemini AI
- 🤖 **AI-powered skill extraction** using structured data
- 🎨 **Devicon icons** for technologies and tools
- 📦 **ZIP file generation** with README + instructions
- ✏️ **Edit and regenerate** functionality
- 🔧 **Multiple LLM providers** (Gemini, Cohere)
- 📊 **Conversation state management**
- 🛡️ **Input validation and error handling**

## 📋 Prerequisites

- Python 3.10+
- Telegram Bot Token
- Gemini API Key (Primary)
- Supabase Project (for database)
- GitHub Personal Access Token (for auto-deploy)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GitHub-Bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Required - Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Required - AI
GEMINI_API_KEY=your_gemini_api_key_here
COHERE_API_KEY=your_cohere_api_key_here  # Optional secondary provider
GROQ_API_KEY=your_groq_api_key_here      # Optional

# Required - Database
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional (for enhanced features)
```

### 4. Get Required API Keys

#### Telegram Bot Token

1. Start a chat with [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token provided

#### Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key and copy it

#### Cohere API Key (Optional)

1. Go to [Cohere Dashboard](https://dashboard.cohere.com/)
2. Sign up and verify your account
3. Navigate to API keys
4. Create a new API key

## 🏃‍♂️ Running the Bot

### Method 1: Direct Run

```bash
python bot/main.py
```

### Method 2: Using Python Module

```bash
python -m bot.main
```

## 📁 Project Structure

```
GitHub-Bot/
├── bot/
│   ├── handlers/
│   │   ├── start_handler.py       # Welcome and onboarding
│   │   ├── info_handler.py        # User data collection
│   │   ├── voice_handler.py       # Voice message processing
│   │   └── confirm_handler.py     # Confirmation and ZIP generation
│   ├── main.py                    # Bot entry point
│   ├── router.py                  # Command and callback routing
│   └── states.py                   # Conversation state management
├── services/
│   ├── prompt_engine.py           # AI prompt templates
│   ├── llm/                       # Language Model providers
│   │   ├── LLMInterface.py        # LLM interface
│   │   ├── LLMProviderFactory.py  # LLM factory pattern
│   │   └── providers/
│   │       ├── GeminiProvider.py  # Gemini AI integration
│   │       └── CohereProvider.py  # Cohere AI integration
│   └── stt/                       # Speech-to-Text providers
│       ├── STTInterface.py        # STT interface
│       ├── STTProviderFactory.py  # STT factory pattern
│       └── providers/
│           └── GeminiProvider.py  # Gemini STT integration
├── utils/
│   ├── logger.py                  # Centralized logging
│   ├── validators.py              # Input validation
│   └── markdown.py               # README generation
├── devicon/
│   ├── resolver.py                # Devicon icon management
│   └── devicon.json              # Devicon database
├── outputs/
│   ├── readmes/                  # Generated README files
│   └── zips/                     # ZIP archives
├── logs/                        # Application logs
├── requirements.txt             # Python dependencies
├── .env                        # Environment variables
└── README.md                   # This file
```

## 🎯 How It Works

### User Flow

1. **Start**: User sends `/start` to begin
2. **Collection**: Bot collects name, GitHub, LinkedIn, portfolio, email
3. **Input**: User sends voice message or text about experience
4. **Processing**: AI extracts structured data (skills, tools, languages)
5. **Review**: User reviews extracted information
6. **Generation**: Bot generates README with Devicon icons
7. **Delivery**: User receives ZIP file with README + instructions

### Technical Flow

1. **STT Processing**: Voice → Text using Gemini
2. **LLM Extraction**: Text → Structured JSON data
3. **Icon Mapping**: Skills → Devicon icons
4. **Markdown Generation**: Data → Professional README
5. **ZIP Creation**: README + Instructions → ZIP file

## 🔧 Configuration

### Environment Variables

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
GEMINI_API_KEY=your_gemini_api_key
COHERE_API_KEY=your_cohere_api_key
```

### Supported LLM Providers

- **Gemini** (Google): Default, supports both STT and LLM
- **Cohere**: LLM-only, requires separate STT provider

### Supported Audio Formats

- `.mp3`, `.wav`, `.ogg`, `.oga`, `.m4a`, `.flac`

## 📊 Features in Detail

### 🎤 Voice Processing

- Automatic transcription using Gemini AI
- Support for multiple audio formats
- Temporary file cleanup
- Error handling for failed transcriptions

### 🤖 AI-Powered Extraction

- Structured data extraction with JSON schema
- Skill categorization (skills, tools, languages)
- Automatic validation and cleaning
- Support for multiple LLM providers

### 🎨 Devicon Integration

- 1000+ technology icons
- Automatic icon URL generation
- Caching for performance
- Fallback to text if icon not found

### 📦 ZIP Generation

- README.md with professional formatting
- INSTRUCTIONS.md with setup guide
- Contact information placeholders
- GitHub stats integration

### ✏️ Edit & Regenerate

- Review extracted information
- Edit skills and details
- Regenerate README with corrections
- Multiple iteration support

## 🛠️ Development

### Adding New Features

1. **New Handlers**: Create in `bot/handlers/`
2. **Register**: Add to `bot/router.py`
3. **Services**: Add to `services/`
4. **Utilities**: Add to `utils/`

### Code Architecture

- **Provider Pattern**: For LLM/STT services
- **Factory Pattern**: For provider selection
- **State Machine**: For conversation flow
- **Interface Segregation**: Clean abstractions

### Testing

```bash
# Test voice processing
python -m bot.handlers.voice_handler

# Test LLM extraction
python -m services.llm.providers.GeminiProvider

# Test Devicon resolution
python -m devicon.resolver
```

## 🔍 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'bot'"**
   - Run from project root: `python bot/main.py`
   - Check Python path configuration

2. **"TELEGRAM_BOT_TOKEN not found"**
   - Verify `.env` file exists
   - Check token format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

3. **"No LLM API keys found"**
   - Set `GEMINI_API_KEY` in .env
   - Restart bot after updating

4. **"Supabase connection failed"**
   - Check `SUPABASE_URL` and `SUPABASE_KEY`
   - Ensure you are using the Service Role Key (not Anon) for full access if needed

5. **"GitHub 404 Error (Snake Animation)"**
   - Ensure your GitHub Token has `workflow` scope
   - Verify the snake.yml template exists in `resources/templates/`
   - Wait a few seconds between README upload and workflow creation

6. **"Could not extract structured data"**
   - Provide more detailed input
   - Check LLM provider status
   - Verify input length (min 50 characters)

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python bot/main.py
```

### Dependencies

```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Check specific packages
pip show python-telegram-bot google-generativeai cohere
```

## 📈 Monitoring

### Logs

- Location: `logs/github_bot_YYYYMMDD.log`
- Format: `timestamp - module - level - message`
- Rotation: Daily log files

### Performance

- Devicon caching with LRU cache
- Temporary file cleanup
- Conversation state management
- Error recovery mechanisms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Include error handling

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:

1. Check the logs in `logs/` directory
2. Review this setup guide
3. Create an issue in the repository
4. Include error messages and logs

---

**Bot Commands:**

- `/start` - Begin README generation
- `/help` - Show help information

**Ready to create professional GitHub READMEs? 🚀**
