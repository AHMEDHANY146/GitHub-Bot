# GitHub-Bot

🤖 A sophisticated Telegram bot that converts voice messages into professional GitHub README files using AI-powered speech-to-text and language models with unified design and comprehensive devicon integration.

## ✨ Features

- 🎤 **Voice Processing**: Convert voice messages to text using advanced STT services
- 🤖 **AI-Powered**: Leverages multiple LLM providers (Cohere, Gemini) for intelligent content generation
- 📝 **README Generation**: Automatically creates professional GitHub README files in markdown format
- 🎨 **Devicon Integration**: Maps technical skills to appropriate devicons for visual enhancement
- 🌸 **Unified Design**: Consistent, modern design across all generated READMEs with flowers/features
- 📬 **Contact Priority**: LinkedIn and Email prominently displayed at the top
- 🔄 **Multi-Provider Support**: Configurable STT and LLM providers for flexibility
- 📊 **Structured Output**: Generates well-organized markdown with proper formatting
- 🏷️ **Smart Icon Mapping**: Comprehensive skill-to-icon mapping with fallbacks

## Project Structure

```
GitHub-Bot/
├── .env.example                    # Environment variables 
├── .gitignore                      # Git ignore rules
├── LICENSE                         # Project license
├── README.md                       # This file
│
├── bot/                            # Telegram bot interface
│   ├── __init__.py
│   ├── main.py                     # Bot entry point
│   ├── router.py                   # Handler registration
│   ├── states.py                   # Conversation states
│   ├── utils.py                    # Bot utilities
│   └── handlers/                   # Bot command handlers
│       ├── __init__.py
│       ├── start_handler.py        # Start command handler
│       ├── info_handler.py         # Information handler
│       ├── voice_handler.py        # Voice message processing
│       └── confirm_handler.py      # Confirmation handlers
│
├── helpers/                        # Configuration and helpers
│   └── config.py                   # Global configuration
│
├── services/                       # Core application logic
│   ├── __init__.py
│   ├── prompt_engine.py           # Central prompt building
│   ├── llm/                       # Language Model abstraction
│   │   ├── __init__.py
│   │   ├── LLMInterface.py        # LLM provider interface
│   │   ├── LLMEnums.py           # LLM provider enums
│   │   ├── LLMProviderFactory.py  # LLM provider factory
│   │   └── providers/             # LLM provider implementations
│   │       ├── __init__.py
│   │       ├── CohereProvider.py
│   │       └── GeminiProvider.py
│   └── stt/                       # Speech-to-Text abstraction
│       ├── __init__.py
│       ├── STTInterface.py        # STT provider interface
│       ├── STTEnums.py           # STT provider enums
│       ├── STTProviderFactory.py  # STT provider factory
│       └── providers/             # STT provider implementations
│           ├── __init__.py
│           └── GeminiProvider.py
│
├── utils/                         # General utilities
│   ├── __init__.py
│   ├── logger.py                  # Central logger configuration
│   ├── validators.py              # Input validation utilities
│   └── markdown.py                # Markdown formatting helpers
│
├── devicon/                       # Devicon integration
│   ├── __init__.py
│   ├── devicon.json               # Devicon metadata cache
│   └── resolver.py                # Skills to devicon mapping
│
└── outputs/                       # Generated files storage
    ├── readmes/                   # Generated README files
    └── zips/                      # Generated zip archives
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd GitHub-Bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Run the bot:
   ```bash
   python bot/main.py
   ```

## Configuration

The bot requires the following environment variables:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
- `COHERE_API_KEY`: Cohere API key (if using Cohere provider)
- `GEMINI_API_KEY`: Google Gemini API key (if using Gemini provider)

## Usage

1. Start a conversation with the bot on Telegram
2. Send a voice message describing yourself or your project
3. The bot will process your voice input and generate a professional README
4. Review and confirm the generated content
5. Receive the final README file in markdown format

## Architecture

The bot follows a modular architecture with clear separation of concerns:

- **Bot Layer**: Handles Telegram interactions and user conversations
- **Services Layer**: Contains core business logic for STT and LLM operations
- **Utilities Layer**: Provides shared functionality across the application
- **Devicon Integration**: Enhances generated content with appropriate tech icons

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.
