# Sag Ine AI Assistant

An intelligent AI assistant with advanced personalization, service integrations, and AI-powered features.

## Features

### Core Features
- Multi-provider AI support (OpenAI, Google Gemini, Ollama)
- Modern and responsive GUI
- File analysis capabilities
- Web search integration

### New Features
- **Personalization**
  - Customizable themes and appearance
  - Adjustable AI behavior and preferences
  - Custom assistant name and chat style

- **Service Integrations**
  - Google Calendar integration
  - Gmail integration
  - Google Sheets support
  - More integrations coming soon!

- **AI-Driven Features**
  - Context-aware responses
  - Personalized recommendations
  - Multiple AI model support

<<<<<<< Updated upstream
1. Clone the repository:
```bash
git clone https://github.com//SagineBM/sag-ine.git
cd sag-ine
```
=======
## Setup
>>>>>>> Stashed changes

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Google Cloud Project:
   - Create a project in Google Cloud Console
   - Enable Calendar, Gmail, and Sheets APIs
   - Create OAuth 2.0 credentials
   - Download credentials as `credentials.json` and place in project root

3. Configure AI providers:
   - Set up API keys in environment variables or config file
   - Supported providers: OpenAI, Google Gemini, Ollama

4. Run the application:
   ```bash
   python ai_assistant_gui.py
   ```

## Configuration

### User Preferences
User preferences are stored in `user_preferences.json` and include:
- Theme settings
- Font preferences
- Language options
- AI model preferences
- Integration settings

### Service Integration
- Requires Google OAuth2 authentication
- First-time setup will prompt for authorization
- Credentials are securely stored for future use

<<<<<<< Updated upstream
## Project Structure

- `ai_assistant_gui.py`: Main GUI application using CustomTkinter
- `ai_providers.py`: Implementation of different AI providers
- `config_manager.py`: Configuration management
- `file_handlers.py`: File operations handling
- `web_search.py`: Web search functionality
- `create_shortcut.py`: Desktop shortcut creation
- `setup.py`: Installation setup script

## Usage

1. Run the application:
```bash
python ai_assistant_gui.py
```

2. Select your preferred AI provider from the dropdown menu
3. Configure the provider settings using the "Configure" button
4. Use the chat interface to interact with the AI
5. Analyze files using the "Analyze File" button

## Features in Detail

### AI Providers

1. **Ollama Provider**
   - Local AI model integration
   - Configurable host and port
   - Custom model selection

2. **OpenAI Provider**
   - GPT-3.5 Turbo integration
   - API key configuration
   - Advanced text generation

3. **Google Gemini Provider**
   - Google's Gemini Pro model
   - API key configuration
   - Robust error handling

4. **Web-Only Provider**
   - Basic web search functionality
   - No API key required
   - Fallback option

### User Interface

- Dark mode theme
- Split-pane layout
- Input/Output text areas
- File analysis capabilities
- Provider configuration panel
=======
## Security
- API keys and credentials are securely stored
- OAuth2 authentication for Google services
- No sensitive data is stored in plain text
>>>>>>> Stashed changes

## Contributing
Contributions are welcome! Please feel free to submit pull requests.
