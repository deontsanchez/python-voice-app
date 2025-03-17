from elevenlabs import generate, save, set_api_key, voices, Voice, VoiceSettings
from src.utils.config import ELEVEN_LABS_API_KEY, DEFAULT_STABILITY, DEFAULT_SIMILARITY, OUTPUT_DIR
import os
import time
from typing import Optional, List, Tuple, Union, Iterator, cast

# Set the API key from config only if it's not None
if ELEVEN_LABS_API_KEY:
    set_api_key(ELEVEN_LABS_API_KEY)
else:
    print("Warning: No API key found. You will not be able to use the Eleven Labs API.")

class TextToSpeech:
    def __init__(self):
        self.available_voices = None
        self.current_voice = None
        self.stability = DEFAULT_STABILITY
        self.similarity = DEFAULT_SIMILARITY
        
    def fetch_available_voices(self):
        """Fetch all available voices from Eleven Labs API"""
        try:
            self.available_voices = voices()
            return self.available_voices
        except Exception as e:
            print(f"Error fetching voices: {e}")
            return []
    
    def set_voice(self, voice_id):
        """Set the current voice by ID"""
        if not self.available_voices:
            self.fetch_available_voices()
        
        # Check if available_voices is None or empty after fetch attempt
        if not self.available_voices:
            print("No voices available")
            return False
            
        for voice in self.available_voices:
            if voice.voice_id == voice_id:
                self.current_voice = voice
                return True
        
        print(f"Voice with ID {voice_id} not found")
        return False
    
    def set_stability(self, stability):
        """Set the stability parameter (0-1)"""
        self.stability = max(0, min(1, stability))
    
    def set_similarity(self, similarity):
        """Set the similarity enhancement parameter (0-1)"""
        self.similarity = max(0, min(1, similarity))
    
    def generate_speech(self, text, save_to_file=True, filename=None) -> Optional[str]:
        """Generate speech from text using the current voice and settings"""
        if not text:
            print("Error: No text provided")
            return None
            
        if not self.current_voice and self.available_voices:
            # Use the first available voice if none selected
            self.current_voice = self.available_voices[0]
        
        if not self.current_voice:
            print("Error: No voice selected and no voices available")
            return None
            
        try:
            # For elevenlabs 0.2.24, let's try without explicit settings
            # Generate the audio with just the voice and text
            audio = generate(
                text=text,
                voice=self.current_voice,
                model="eleven_monolingual_v1"
            )
            
            # Save the audio to a file if requested
            if save_to_file:
                if not filename:
                    timestamp = int(time.time())
                    filename = f"speech_{timestamp}.mp3"
                
                file_path = os.path.join(OUTPUT_DIR, filename)
                # Cast audio to bytes to satisfy the type checker
                save(cast(bytes, audio), file_path)
                print(f"Audio saved to {file_path}")
                return file_path
            
            # If not saving to file, shouldn't be used with file operations
            return None
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None
    
    def get_voice_names(self):
        """Get a list of voice names for the UI"""
        if not self.available_voices:
            self.fetch_available_voices()
            
        # Check if available_voices is None or empty after fetch attempt
        if not self.available_voices:
            return []
            
        return [(voice.name, voice.voice_id) for voice in self.available_voices] 