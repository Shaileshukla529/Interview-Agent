import boto3
import os
import tempfile
import pygame
import time
from .config import Config

class PollyHandler:
    """Handle Text-to-Speech using AWS Polly."""
    
    def __init__(self):
        self.client = boto3.client('polly', region_name='us-east-1') # Default region, can be configured
        self.voice_id = "Joanna" # Neural voice
        self.engine = "neural"
        
        # Initialize pygame mixer for playback
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Warning: Could not initialize audio mixer: {e}")

    def speak(self, text: str):
        """Synthesize speech and play it."""
        if not text:
            return

        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )

            if "AudioStream" in response:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    f.write(response['AudioStream'].read())
                    temp_filename = f.name

                # Play audio
                self._play_audio(temp_filename)
                
                # Cleanup
                try:
                    os.remove(temp_filename)
                except:
                    pass
            else:
                print("Error: No AudioStream in Polly response")

        except Exception as e:
            print(f"Polly Error: {e}")

    def _play_audio(self, filename):
        """Play audio file using pygame."""
        try:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.music.unload()
        except Exception as e:
            print(f"Audio Playback Error: {e}")
