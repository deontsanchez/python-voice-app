import tkinter as tk
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path to make imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our application's window class
from src.gui.app_window import AppWindow

# Load environment variables
load_dotenv()

# Check if the API key is set
if not os.getenv("ELEVEN_LABS_API_KEY"):
    print("Warning: ELEVEN_LABS_API_KEY not found in environment variables.")
    print("Please create a .env file with your API key or set it in your environment.")

def main():
    # Create the root window
    root = tk.Tk()
    
    # Set the window icon if available
    try:
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
        if os.path.exists(logo_path):
            logo = tk.PhotoImage(file=logo_path)
            root.iconphoto(True, logo)
    except Exception as e:
        print(f"Warning: Could not set app icon: {e}")
    
    # Apply a theme (if available)
    try:
        from tkinter import ttk
        style = ttk.Style()
        
        # Try to use a modern theme if available
        available_themes = style.theme_names()
        preferred_themes = ["clam", "alt", "vista", "xpnative"]
        
        for theme in preferred_themes:
            if theme in available_themes:
                style.theme_use(theme)
                break
    except Exception as e:
        print(f"Warning: Could not apply theme: {e}")
    
    # Create the application window
    app = AppWindow(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 