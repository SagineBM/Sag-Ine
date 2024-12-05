import requests
import json
from abc import ABC, abstractmethod
import google.generativeai as genai
import openai

class AIProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

    @abstractmethod
    def analyze_file(self, file_content: str, file_type: str) -> str:
        pass

class OllamaProvider(AIProvider):
    def __init__(self, host: str, port: str, model: str):
        self.base_url = f"{host}:{port}"
        self.model = model

    def generate_response(self, prompt: str) -> str:
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
                return full_response
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def generate_response(self, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error with OpenAI: {str(e)}"

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.max_retries = 3
        self.base_delay = 2  # seconds

    def generate_response(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                error_str = str(e).lower()
                if "rate limit" in error_str:
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                        import time
                        time.sleep(delay)
                        continue
                    return ("Rate limit exceeded. Please wait a few minutes before trying again. "
                           "You can temporarily switch to another AI provider or web-only mode.")
                return f"Error with Gemini: {str(e)}"
        return "Maximum retries exceeded. Please try again later."

    def analyze_file(self, file_content: str, file_type: str) -> str:
        prompt = f"Please analyze this {file_type} content:\n\n{file_content}"
        return self.generate_response(prompt)

class WebOnlyProvider(AIProvider):
    def generate_response(self, prompt: str) -> str:
        return "Web-only mode does not provide AI responses. Please use the web search feature."

    def analyze_file(self, file_content: str, file_type: str) -> str:
        return "File analysis is not available in web-only mode. Please configure an AI provider."
