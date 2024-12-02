# Sag Ine - AI Assistant GUI

Sag Ine is a versatile AI assistant application with a modern graphical user interface built using CustomTkinter. It supports multiple AI providers and offers file analysis capabilities along with interactive chat functionality.

## Features

- 🤖 Multiple AI Provider Support
  - Ollama (local AI)
  - OpenAI
  - Google Gemini
  - Web-only mode
- 🎨 Modern Dark Theme Interface
- 📁 File Analysis Capabilities
- ⚙️ Configurable Settings
- 💬 Interactive Chat Interface

## Requirements

- Python 3.x
- CustomTkinter
- Pillow (PIL)
- Requests
- BeautifulSoup4
- Google Generative AI
- OpenAI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sag-ine.git
cd sag-ine
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses a configuration file (`sag_ine_config.json`) to store settings for different AI providers. You can configure:

- AI Provider selection (ollama, openai, gemini, none)
- API keys for OpenAI and Google Gemini
- Ollama host and port settings
- Model selection for Ollama

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- CustomTkinter for the modern UI components
- Various AI providers for their APIs and services
