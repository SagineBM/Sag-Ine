import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
from bs4 import BeautifulSoup
import json
from tkinter import messagebox
import threading
import customtkinter as ctk
import os
from PIL import Image, ImageTk
from config_manager import ConfigManager
from ai_providers import OllamaProvider, OpenAIProvider, GeminiProvider, WebOnlyProvider
from file_handlers import FileHandler
from web_search import search_web

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AIAssistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = ConfigManager()
        self.setup_ai_provider()
        
        # Configure window
        self.title("Sag Ine")
        self.geometry("1200x800")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create frames
        self.create_top_frame()
        self.create_main_frame()
        self.create_bottom_frame()
        
        # Initialize file analysis variables
        self.current_file = None
        self.file_content = None

    def setup_ai_provider(self):
        provider = self.config.get_ai_provider()
        if provider == "ollama":
            settings = self.config.get_ollama_settings()
            self.ai_provider = OllamaProvider(settings["host"], settings["port"], settings["model"])
        elif provider == "openai":
            api_key = self.config.get_api_key("openai")
            self.ai_provider = OpenAIProvider(api_key)
        elif provider == "gemini":
            api_key = self.config.get_api_key("gemini")
            self.ai_provider = GeminiProvider(api_key)
        else:
            self.ai_provider = WebOnlyProvider()
    
    def create_top_frame(self):
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # AI Provider selection
        provider_label = ctk.CTkLabel(top_frame, text="AI Provider:")
        provider_label.pack(side="left", padx=5)
        
        self.provider_var = ctk.StringVar(value=self.config.get_ai_provider())
        provider_menu = ctk.CTkOptionMenu(
            top_frame,
            values=["none", "ollama", "openai", "gemini"],
            variable=self.provider_var,
            command=self.change_provider
        )
        provider_menu.pack(side="left", padx=5)
        
        # Configure button
        config_btn = ctk.CTkButton(top_frame, text="Configure", command=self.show_config_window)
        config_btn.pack(side="left", padx=5)
        
        # File analysis button
        analyze_btn = ctk.CTkButton(top_frame, text="Analyze File", command=self.select_file)
        analyze_btn.pack(side="right", padx=5)
    
    def create_main_frame(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Input frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.input_text = ctk.CTkTextbox(input_frame, height=100)
        self.input_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Output frame
        output_frame = ctk.CTkFrame(main_frame)
        output_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.output_text = ctk.CTkTextbox(output_frame)
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_bottom_frame(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Search mode selection
        self.search_mode = ctk.StringVar(value="both")
        
        ai_radio = ctk.CTkRadioButton(bottom_frame, text="AI Only", variable=self.search_mode, value="ai")
        ai_radio.pack(side="left", padx=5)
        
        web_radio = ctk.CTkRadioButton(bottom_frame, text="Web Only", variable=self.search_mode, value="web")
        web_radio.pack(side="left", padx=5)
        
        both_radio = ctk.CTkRadioButton(bottom_frame, text="Both", variable=self.search_mode, value="both")
        both_radio.pack(side="left", padx=5)
        
        # Search button
        search_btn = ctk.CTkButton(bottom_frame, text="Search", command=self.search)
        search_btn.pack(side="right", padx=5)
        
        # Clear button
        clear_btn = ctk.CTkButton(bottom_frame, text="Clear", command=self.clear)
        clear_btn.pack(side="right", padx=5)
    
    def show_config_window(self):
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configure AI Provider")
        config_window.geometry("400x300")
        
        provider = self.provider_var.get()
        
        if provider == "ollama":
            # Ollama configuration
            host_label = ctk.CTkLabel(config_window, text="Host:")
            host_label.pack(pady=5)
            host_entry = ctk.CTkEntry(config_window)
            host_entry.insert(0, self.config.get_ollama_settings()["host"])
            host_entry.pack(pady=5)
            
            port_label = ctk.CTkLabel(config_window, text="Port:")
            port_label.pack(pady=5)
            port_entry = ctk.CTkEntry(config_window)
            port_entry.insert(0, self.config.get_ollama_settings()["port"])
            port_entry.pack(pady=5)
            
            model_label = ctk.CTkLabel(config_window, text="Model:")
            model_label.pack(pady=5)
            model_entry = ctk.CTkEntry(config_window)
            model_entry.insert(0, self.config.get_ollama_settings()["model"])
            model_entry.pack(pady=5)
            
            def save_ollama():
                self.config.set_ollama_settings(
                    host_entry.get(),
                    port_entry.get(),
                    model_entry.get()
                )
                self.setup_ai_provider()
                config_window.destroy()
            
            save_btn = ctk.CTkButton(config_window, text="Save", command=save_ollama)
            save_btn.pack(pady=20)
            
        elif provider in ["openai", "gemini"]:
            # API key configuration
            key_label = ctk.CTkLabel(config_window, text="API Key:")
            key_label.pack(pady=5)
            key_entry = ctk.CTkEntry(config_window, show="*")
            key_entry.insert(0, self.config.get_api_key(provider))
            key_entry.pack(pady=5)
            
            def save_api_key():
                self.config.set_api_key(provider, key_entry.get())
                self.setup_ai_provider()
                config_window.destroy()
            
            save_btn = ctk.CTkButton(config_window, text="Save", command=save_api_key)
            save_btn.pack(pady=20)
    
    def change_provider(self, provider):
        self.config.set_ai_provider(provider)
        self.setup_ai_provider()
    
    def select_file(self):
        file_types = [
            ("All supported files", "*.txt;*.docx;*.pdf;*.csv;*.xlsx;*.xls"),
            ("Text files", "*.txt"),
            ("Word documents", "*.docx"),
            ("PDF files", "*.pdf"),
            ("Spreadsheets", "*.csv;*.xlsx;*.xls")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select a file to analyze",
            filetypes=file_types
        )
        
        if filename:
            try:
                self.current_file = filename
                self.file_content, file_type = FileHandler.read_file(filename)
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", f"Analyzing {file_type} file: {filename}\n\n")
                self.search()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def search(self):
        query = self.input_text.get("1.0", "end").strip()
        mode = self.search_mode.get()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a query or select a file to analyze.")
            return
        
        self.output_text.delete("1.0", "end")
        self.output_text.insert("end", "Searching...\n\n")
        
        def search_thread():
            results = []
            
            if mode in ["ai", "both"] and isinstance(self.ai_provider, WebOnlyProvider):
                results.append("AI search is not available. Please configure an AI provider.")
            elif mode in ["ai", "both"]:
                if self.file_content:
                    ai_response = self.ai_provider.analyze_file(self.file_content, "file")
                else:
                    ai_response = self.ai_provider.generate_response(query)
                results.append(f"AI Response:\n{ai_response}\n")
            
            if mode in ["web", "both"]:
                web_results = search_web(query)
                results.append(f"\nWeb Search Results:\n{web_results}")
            
            self.output_text.delete("1.0", "end")
            for result in results:
                self.output_text.insert("end", result + "\n")
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def clear(self):
        self.input_text.delete("1.0", "end")
        self.output_text.delete("1.0", "end")
        self.current_file = None
        self.file_content = None

if __name__ == "__main__":
    app = AIAssistantGUI()
    app.mainloop()
