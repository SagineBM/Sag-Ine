import requests
import json
from abc import ABC, abstractmethod
import google.generativeai as genai
import openai

class AIProvider(ABC):
    def __init__(self):
        self.capabilities = {
            'streaming': False,
            'file_analysis': False,
            'code_completion': False,
            'multimodal': False
        }
        self._response_cache = {}
        self.max_retries = 3
        self.base_delay = 2

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def analyze_file(self, file_content: str, file_type: str) -> str:
        pass

    def supports_capability(self, capability: str) -> bool:
        return self.capabilities.get(capability, False)

    def _cached_response(self, prompt: str) -> str | None:
        return self._response_cache.get(prompt)

    def _cache_response(self, prompt: str, response: str):
        self._response_cache[prompt] = response
        if len(self._response_cache) > 1000:  # Prevent unlimited growth
            self._response_cache.pop(next(iter(self._response_cache)))

    def _handle_rate_limit(self, attempt: int) -> bool:
        if attempt < self.max_retries - 1:
            delay = self.base_delay * (2 ** attempt)
            import time
            time.sleep(delay)
            return True
        return False

    def _handle_error(self, e: Exception, context: str) -> str:
        error_type = type(e).__name__
        error_str = str(e).lower()
        
        if "rate limit" in error_str:
            return f"Rate limit exceeded in {context}. Please try again later."
        elif "authentication" in error_str or "api key" in error_str:
            return f"Authentication error in {context}. Please check your API key."
        elif "connection" in error_str:
            return f"Connection error in {context}. Please check your internet connection."
        else:
            return f"Error in {context}: {error_type} - {str(e)}"

class OllamaProvider(AIProvider):
    def __init__(self, host: str, port: str, model: str):
        super().__init__()
        self.base_url = f"{host}:{port}"
        self.model = model
        self.capabilities['streaming'] = True

    def generate_response(self, prompt: str) -> str:
        cached_response = self._cached_response(prompt)
        if cached_response:
            return cached_response

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt},
                stream=True
            )
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            json_response = json.loads(line)
                            if 'response' in json_response:
                                full_response += json_response['response']
                        except json.JSONDecodeError:
                            continue
                self._cache_response(prompt, full_response)
                return full_response
            return f"Error: {response.status_code}"
        except Exception as e:
            return self._handle_error(e, "Ollama")

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__()
        openai.api_key = api_key
        self.capabilities['code_completion'] = True

    def generate_response(self, prompt: str) -> str:
        cached_response = self._cached_response(prompt)
        if cached_response:
            return cached_response

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            self._cache_response(prompt, response.choices[0].message.content)
            return response.choices[0].message.content
        except Exception as e:
            return self._handle_error(e, "OpenAI")

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.capabilities['multimodal'] = True

    def generate_response(self, prompt: str) -> str:
        cached_response = self._cached_response(prompt)
        if cached_response:
            return cached_response

        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                self._cache_response(prompt, response.text)
                return response.text
            except Exception as e:
                if self._handle_rate_limit(attempt):
                    continue
                return self._handle_error(e, "Gemini")

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class WebOnlyProvider(AIProvider):
    def generate_response(self, prompt: str) -> str:
        return "Web-only mode does not provide AI responses. Please use the web search feature."

    def analyze_file(self, file_content: str, file_type: str) -> str:
        return "File analysis is not available in web-only mode. Please configure an AI provider."
