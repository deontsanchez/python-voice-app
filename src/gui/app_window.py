import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import threading
import pygame
from PIL import Image, ImageTk
from typing import Optional

from src.utils.tts import TextToSpeech
from src.utils.config import OUTPUT_DIR

class AppWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Eleven Labs Text-to-Speech")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize the TTS engine
        self.tts = TextToSpeech()
        
        # Initialize pygame for audio playback
        # Initialize only the mixer module, not the entire pygame
        pygame.mixer.init()
        
        # Track current audio file
        self.current_audio_file: Optional[str] = None
        self.is_playing = False
        
        # Create the UI elements
        self.create_ui()
        
        # Fetch available voices in a separate thread to avoid blocking the UI
        threading.Thread(target=self.load_voices, daemon=True).start()
    
    def create_ui(self):
        """Create all UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Voice selection frame
        voice_frame = ttk.LabelFrame(main_frame, text="Voice Settings", padding=10)
        voice_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Voice dropdown
        ttk.Label(voice_frame, text="Select Voice:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.voice_var = tk.StringVar()
        self.voice_dropdown = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly", width=30)
        self.voice_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.voice_dropdown.bind("<<ComboboxSelected>>", self.on_voice_selected)
        
        # Stability slider
        ttk.Label(voice_frame, text="Stability:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.stability_var = tk.DoubleVar(value=0.5)
        stability_slider = ttk.Scale(voice_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                                     variable=self.stability_var, length=200)
        stability_slider.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        stability_slider.bind("<ButtonRelease-1>", lambda e: self.on_stability_changed())
        
        # Similarity slider
        ttk.Label(voice_frame, text="Similarity:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.similarity_var = tk.DoubleVar(value=0.75)
        similarity_slider = ttk.Scale(voice_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, 
                                      variable=self.similarity_var, length=200)
        similarity_slider.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        similarity_slider.bind("<ButtonRelease-1>", lambda e: self.on_similarity_changed())
        
        # Text input frame
        text_frame = ttk.LabelFrame(main_frame, text="Text Input", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text area
        self.text_input = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Generate button
        self.generate_btn = ttk.Button(button_frame, text="Generate Speech", command=self.generate_speech)
        self.generate_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Play button
        self.play_btn = ttk.Button(button_frame, text="Play", command=self.play_audio, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_audio, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Save button
        self.save_btn = ttk.Button(button_frame, text="Save Audio File", command=self.save_audio, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
    
    def load_voices(self):
        """Load available voices and update the dropdown"""
        self.status_var.set("Loading voices...")
        voices = self.tts.get_voice_names()
        
        # Update UI in the main thread
        self.root.after(0, lambda: self.update_voice_dropdown(voices))
    
    def update_voice_dropdown(self, voices):
        """Update the voice dropdown with the fetched voices"""
        if not voices:
            self.status_var.set("No voices found. Check your API key.")
            return
            
        voice_options = [f"{name}" for name, _ in voices]
        self.voice_dropdown['values'] = voice_options
        self.voice_dropdown.current(0)
        self.voice_ids = [voice_id for _, voice_id in voices]
        self.on_voice_selected(None)
        self.status_var.set(f"Loaded {len(voices)} voices")
    
    def on_voice_selected(self, event):
        """Handle voice selection from dropdown"""
        if not hasattr(self, 'voice_ids'):
            return
            
        selected_index = self.voice_dropdown.current()
        if selected_index >= 0:
            voice_id = self.voice_ids[selected_index]
            self.tts.set_voice(voice_id)
            self.status_var.set(f"Selected voice: {self.voice_dropdown.get()}")
    
    def on_stability_changed(self):
        """Handle stability slider change"""
        stability = self.stability_var.get()
        self.tts.set_stability(stability)
        self.status_var.set(f"Stability set to {stability:.2f}")
    
    def on_similarity_changed(self):
        """Handle similarity slider change"""
        similarity = self.similarity_var.get()
        self.tts.set_similarity(similarity)
        self.status_var.set(f"Similarity set to {similarity:.2f}")
    
    def generate_speech(self):
        """Generate speech from the text input"""
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert to speech.")
            return
        
        # Disable buttons during generation
        self.generate_btn.config(state=tk.DISABLED)
        self.status_var.set("Generating speech...")
        
        # Run generation in a separate thread to avoid freezing the UI
        threading.Thread(target=self.generate_speech_thread, args=(text,), daemon=True).start()
    
    def generate_speech_thread(self, text):
        """Thread function for speech generation"""
        try:
            audio_file = self.tts.generate_speech(text)
            if audio_file and isinstance(audio_file, str):
                self.current_audio_file = audio_file
                # Update UI in the main thread
                self.root.after(0, self.enable_audio_buttons)
                self.root.after(0, lambda: self.status_var.set(f"Speech generated: {os.path.basename(audio_file)}"))
            else:
                self.root.after(0, lambda: self.status_var.set("Error generating speech"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate speech: {str(e)}"))
        finally:
            # Re-enable generate button
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
    
    def enable_audio_buttons(self):
        """Enable audio control buttons after successful generation"""
        self.play_btn.config(state=tk.NORMAL)
        self.save_btn.config(state=tk.NORMAL)
    
    def play_audio(self):
        """Play the generated audio"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            self.status_var.set("No audio file available")
            return
        
        if self.is_playing:
            pygame.mixer.music.unpause()
            self.stop_btn.config(state=tk.NORMAL)
            self.play_btn.config(text="Pause")
        else:
            try:
                pygame.mixer.music.load(self.current_audio_file)
                pygame.mixer.music.play()
                self.is_playing = True
                self.play_btn.config(text="Pause")
                self.stop_btn.config(state=tk.NORMAL)
                self.status_var.set(f"Playing: {os.path.basename(self.current_audio_file)}")
                
                # Instead of using pygame events, use tkinter's after to check if music is still playing
                self.root.after(100, self.check_music_end)
            except Exception as e:
                self.status_var.set(f"Error playing audio: {str(e)}")
    
    def check_music_end(self):
        """Check if the music has ended and update UI accordingly"""
        if self.is_playing:
            # Instead of using pygame.event.get(), check if music is playing directly
            if not pygame.mixer.music.get_busy():
                self.stop_audio()
                return
            self.root.after(100, self.check_music_end)
    
    def stop_audio(self):
        """Stop the currently playing audio"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.play_btn.config(text="Play")
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("Playback stopped")
    
    def save_audio(self):
        """Save the generated audio to a user-specified location"""
        if not self.current_audio_file or not os.path.exists(self.current_audio_file):
            self.status_var.set("No audio file available")
            return
        
        # Get a save location from the user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")],
            initialdir=os.path.expanduser("~"),
            title="Save audio file"
        )
        
        if file_path:
            try:
                # If the file already exists, unlink it first
                if os.path.exists(file_path):
                    os.unlink(file_path)
                
                # Copy the file
                import shutil
                shutil.copy2(self.current_audio_file, file_path)
                self.status_var.set(f"Audio saved to: {file_path}")
            except Exception as e:
                self.status_var.set(f"Error saving file: {str(e)}")
                messagebox.showerror("Error", f"Failed to save audio file: {str(e)}") 