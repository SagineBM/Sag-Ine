import json
import os
from typing import Dict, Optional

class ConfigManager:
    def __init__(self):
        self.config_file = "sag_ine_config.json"
        self.default_config = {
            "ai_provider": "none",  # none, ollama, openai, gemini
            "api_keys": {
                "openai": "",
                "gemini": ""
            },
            "ollama": {
                "host": "http://localhost",
                "port": "11434",
                "model": "llama3"
            },
            "theme": "dark",
            "recent_files": []
        }
        self.config = self.load_config()

    def load_config(self) -> Dict:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config.copy()
        return self.default_config.copy()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_ai_provider(self) -> str:
        return self.config.get("ai_provider", "none")

    def set_ai_provider(self, provider: str):
        self.config["ai_provider"] = provider
        self.save_config()

    def get_api_key(self, provider: str) -> str:
        return self.config.get("api_keys", {}).get(provider, "")

    def set_api_key(self, provider: str, key: str):
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}
        self.config["api_keys"][provider] = key
        self.save_config()

    def get_ollama_settings(self) -> Dict:
        return self.config.get("ollama", self.default_config["ollama"])

    def set_ollama_settings(self, host: str, port: str, model: str):
        self.config["ollama"] = {
            "host": host,
            "port": port,
            "model": model
        }
        self.save_config()

    def add_recent_file(self, file_path: str):
        if "recent_files" not in self.config:
            self.config["recent_files"] = []
        if file_path in self.config["recent_files"]:
            self.config["recent_files"].remove(file_path)
        self.config["recent_files"].insert(0, file_path)
        self.config["recent_files"] = self.config["recent_files"][:10]  # Keep only last 10 files
        self.save_config()

    def get_recent_files(self) -> list:
        return self.config.get("recent_files", [])
