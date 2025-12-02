import boto3
import pygame
import io
import time

class PollyHandler:
    """Handle Text-to-Speech using AWS Polly with in-memory playback."""
    
    def __init__(self):
        self.client = boto3.client('polly', region_name='us-east-1')
        self.voice_id = "Matthew" # Changed to Male Neural (optional)
        self.engine = "neural"
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Audio Error: {e}")

    def speak(self, text: str):
        if not text: return

        try:
            response = self.client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice_id,
                Engine=self.engine
            )

            if "AudioStream" in response:
                # Read stream into memory buffer
                audio_stream = io.BytesIO(response['AudioStream'].read())
                self._play_audio(audio_stream)
        except Exception as e:
            print(f"Polly Error: {e}")

    def _play_audio(self, audio_buffer):
        try:
            # Load directly from memory, no file creation needed
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Wait for playback
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Playback Error: {e}")