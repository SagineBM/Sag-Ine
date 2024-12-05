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
from user_preferences import UserPreferences
from service_integrations import ServiceIntegrationManager
import time
from datetime import datetime

# Custom color scheme
THEME = {
    'primary': '#1E88E5',       # Main brand color
    'secondary': '#0D47A1',     # Darker shade for hover states
    'background': '#1a1a1a',    # Dark background
    'surface': '#2b2b2b',       # Slightly lighter background for cards
    'text': '#FFFFFF',          # Primary text color
    'text_secondary': '#B0BEC5' # Secondary text color
}

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hover_animation = None
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        if self.hover_animation:
            self.after_cancel(self.hover_animation)
        self._animate_hover(0)

    def on_leave(self, event):
        if self.hover_animation:
            self.after_cancel(self.hover_animation)
        self._animate_hover(1)

    def _animate_hover(self, direction):
        current_color = self._fg_color
        target_color = THEME['secondary'] if direction == 0 else THEME['primary']
        self.configure(fg_color=target_color)
        
class LoadingDots(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dots = []
        for i in range(3):
            dot = ctk.CTkLabel(self, text="•", text_color=THEME['text'], font=("Helvetica", 24))
            dot.grid(row=0, column=i, padx=2)
            self.dots.append(dot)
        self.current_dot = 0
        self.animate()

    def animate(self):
        for i, dot in enumerate(self.dots):
            if i == self.current_dot:
                dot.configure(text_color=THEME['primary'])
            else:
                dot.configure(text_color=THEME['text_secondary'])
        self.current_dot = (self.current_dot + 1) % 3
        self.after(500, self.animate)

class ChatBubbleFrame(ctk.CTkFrame):
    def __init__(self, master, message, is_user=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Create bubble frame
        bubble_color = THEME['primary'] if is_user else THEME['surface']
        text_color = THEME['text']
        
        bubble = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            corner_radius=20
        )
        
        # Position bubble based on sender
        if is_user:
            bubble.grid(row=0, column=0, padx=(100, 20), pady=5, sticky="e")
        else:
            bubble.grid(row=0, column=0, padx=(20, 100), pady=5, sticky="w")
        
        # Add message text
        label = ctk.CTkLabel(
            bubble,
            text=message,
            text_color=text_color,
            font=("Helvetica", 12),
            wraplength=400,
            justify="left" if not is_user else "right"
        )
        label.pack(padx=15, pady=10)

class ScrollableChatFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

    def add_message(self, message, is_user=True):
        ChatBubbleFrame(self, message, is_user).grid(row=len(self.grid_slaves()), column=0, sticky="ew")
        
        # Scroll to bottom after adding message
        self.after(100, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        try:
            self._parent_canvas.yview_moveto(1.0)
        except:
            pass

    def add_loading_indicator(self):
        loading_frame = LoadingDots(
            self,
            fg_color=THEME['surface'],
            corner_radius=20
        )
        loading_frame.grid(row=len(self.grid_slaves()), column=0, padx=(20, 100), pady=5, sticky="w")
        
        return loading_frame

class AIAssistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config = ConfigManager()
        self.user_prefs = UserPreferences()
        self.service_manager = ServiceIntegrationManager()
        self.setup_ai_provider()
        
        # Initialize request queue and processing flag
        self.request_queue = []
        self.is_processing = False
        self.current_task = None
        
        # Configure window
        self.title(self.user_prefs.get_preference("personalization", "assistant_name"))
        self.geometry("1400x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Set theme based on user preferences
        ctk.set_appearance_mode(self.user_prefs.get_preference("theme"))
        
        # Configure grid for main content and sidebar
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar with enhanced styling
        self.sidebar = ctk.CTkFrame(self, width=80, fg_color=THEME['background'])
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=3)
        self.sidebar.grid_propagate(False)
        
        # Sidebar buttons with new AnimatedButton class
        button_configs = [
            ("⚙️", self.show_config_window, "Settings"),
            ("📁", self.select_file, "Files"),
            ("📅", self.show_calendar, "Calendar"),
            ("📧", self.show_emails, "Email")
        ]
        
        for i, (icon, command, tooltip) in enumerate(button_configs):
            btn = AnimatedButton(
                self.sidebar,
                text=icon,
                width=50,
                height=50,
                fg_color=THEME['primary'],
                hover_color=THEME['secondary'],
                command=command
            )
            btn.grid(row=i, column=0, pady=10, padx=15)
            self._create_tooltip(btn, tooltip)
        
        # Create main content frame with modern styling
        self.main_content = ctk.CTkFrame(self, fg_color=THEME['surface'])
        self.main_content.grid(row=0, column=1, sticky="nsew", rowspan=3)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Enhanced top bar
        self.top_bar = ctk.CTkFrame(self.main_content, fg_color=THEME['background'], height=60)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Styled AI Provider selection
        self.provider_var = ctk.StringVar(value=self.config.get_ai_provider())
        provider_menu = ctk.CTkOptionMenu(
            self.top_bar,
            values=["none", "ollama", "openai", "gemini"],
            variable=self.provider_var,
            command=self.change_provider,
            fg_color=THEME['primary'],
            button_color=THEME['primary'],
            button_hover_color=THEME['secondary'],
            dropdown_hover_color=THEME['secondary']
        )
        provider_menu.pack(side="left", padx=20, pady=10)
        
        # Chat area with enhanced styling
        self.chat_frame = ScrollableChatFrame(
            self.main_content,
            fg_color=THEME['surface'],
            corner_radius=15
        )
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        
        # Modern input frame
        self.input_frame = ctk.CTkFrame(self.main_content, fg_color=THEME['background'], height=80)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # Enhanced input field
        self.input_field = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            fg_color=THEME['surface'],
            text_color=THEME['text'],
            placeholder_text_color=THEME['text_secondary'],
            font=("Helvetica", 14),
            height=50,
            corner_radius=25
        )
        self.input_field.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="ew")
        
        # Modern send button
        self.send_button = AnimatedButton(
            self.input_frame,
            text="Send",
            command=self.send_message,
            fg_color=THEME['primary'],
            hover_color=THEME['secondary'],
            font=("Helvetica", 14, "bold"),
            width=100,
            height=40,
            corner_radius=20
        )
        self.send_button.grid(row=0, column=1, padx=(10, 20), pady=15)
        
        # Bind Enter key
        self.input_field.bind("<Return>", self.send_message)
        
        # Show welcome message with typing animation
        self.after(500, lambda: self._show_welcome_message())

    def _create_tooltip(self, widget, text):
        tooltip = ctk.CTkLabel(
            widget,
            text=text,
            fg_color=THEME['background'],
            corner_radius=6,
            text_color=THEME['text']
        )
        
        def enter(event):
            tooltip.place(x=widget.winfo_width() + 10, y=widget.winfo_height()//2)
            
        def leave(event):
            tooltip.place_forget()
            
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def _show_welcome_message(self):
        welcome_msg = "👋 Hello! I'm your AI assistant. How can I help you today?"
        self.chat_frame.add_message(welcome_msg, is_user=False)

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
                self.chat_frame.add_message(f"Analyzing {file_type} file: {filename}\n\n", is_user=False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def process_queue(self):
        if self.is_processing or not self.request_queue:
            return
        
        self.is_processing = True
        task = self.request_queue.pop(0)
        self.current_task = task
        
        def on_complete(response):
            self.is_processing = False
            self.current_task = None
            self.chat_frame.add_message(response, is_user=False)
            self.after(100, self.process_queue)
        
        thread = threading.Thread(
            target=self._process_task_thread,
            args=(task, on_complete)
        )
        thread.start()

    def _process_task_thread(self, task, callback):
        try:
            response = self.ai_provider.generate_response(task)
            self.after(0, lambda: callback(response))
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            self.after(0, lambda: callback(error_msg))

    def send_message(self, event=None):
        user_input = self.input_field.get()
        if user_input:
            # Add user message
            self.chat_frame.add_message(user_input, is_user=True)
            
            self.input_field.delete(0, 'end')
            query = user_input
            mode = "ai"
            
            if not query:
                messagebox.showwarning("Warning", "Please enter a query or select a file to analyze.")
                return
            
            # Add loading indicator
            loading_frame = self.chat_frame.add_loading_indicator()
            
            # Add to queue and process
            self.request_queue.append(query)
            self.process_queue()
    
    def show_calendar(self):
        if not self.service_manager.credentials:
            if not self.service_manager.authenticate():
                messagebox.showerror("Authentication Error", "Failed to authenticate with Google services")
                return
        
        result = self.service_manager.get_calendar_events()
        if 'error' in result:
            messagebox.showerror("Error", f"Failed to fetch calendar events: {result['error']}")
            return
            
        events = result.get('events', [])
        if events:
            event_window = ctk.CTkToplevel(self)
            event_window.title("Calendar Events")
            event_window.geometry("600x400")
            
            # Create header
            header = ctk.CTkLabel(
                event_window,
                text="Upcoming Calendar Events",
                font=("Helvetica", 16, "bold"),
                text_color=THEME['text']
            )
            header.pack(pady=10)
            
            event_frame = ScrollableChatFrame(event_window)
            event_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            for event in events:
                summary = event.get('summary', 'No Title')
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', 'N/A'))
                location = event.get('location', 'No Location')
                
                # Format the date/time
                try:
                    if 'T' in start:  # DateTime format
                        dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
                    else:  # Date only format
                        dt = datetime.fromisoformat(start)
                        formatted_time = dt.strftime("%B %d, %Y")
                except:
                    formatted_time = start
                
                event_text = f"📅 {summary}\n🕒 {formatted_time}\n📍 {location}"
                event_frame.add_message(event_text, False)
        else:
            messagebox.showinfo("Calendar", "No upcoming events found")

    def show_emails(self):
        if not self.service_manager.credentials:
            if not self.service_manager.authenticate():
                messagebox.showerror("Authentication Error", "Failed to authenticate with Google services")
                return
        
        result = self.service_manager.get_emails()
        if 'error' in result:
            messagebox.showerror("Error", f"Failed to fetch emails: {result['error']}")
            return
            
        emails = result.get('messages', [])
        if emails:
            email_window = ctk.CTkToplevel(self)
            email_window.title("Recent Emails")
            email_window.geometry("600x400")
            
            # Create header
            header = ctk.CTkLabel(
                email_window,
                text="Recent Emails",
                font=("Helvetica", 16, "bold"),
                text_color=THEME['text']
            )
            header.pack(pady=10)
            
            email_frame = ScrollableChatFrame(email_window)
            email_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            for email in emails:
                subject = email.get('subject', 'No Subject')
                sender = email.get('from', 'Unknown Sender')
                date = email.get('date', 'No Date')
                
                try:
                    dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                    formatted_date = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_date = date
                
                email_text = f"📧 {subject}\n👤 From: {sender}\n🕒 {formatted_date}"
                email_frame.add_message(email_text, False)
        else:
            messagebox.showinfo("Email", "No recent emails found")

    def on_closing(self):
        try:
            if hasattr(self, 'ai_provider'):
                self.ai_provider.cleanup()
        except:
            pass
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = AIAssistantGUI()
    app.mainloop()
