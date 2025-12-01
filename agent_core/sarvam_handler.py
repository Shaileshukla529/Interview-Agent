import os
import time
import wave
import tempfile
import pyaudio
import threading
import queue
from sarvamai import SarvamAI
from .config import Config

class SarvamHandler:
    """Handle Speech-to-Text using Sarvam AI (Record & Transcribe)."""
    
    def __init__(self):
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            print("Warning: SARVAM_API_KEY not found")
            self.client = None
        else:
            self.client = SarvamAI(api_subscription_key=api_key)
            
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        
        # Audio config
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.SILENCE_THRESHOLD = 500 # Amplitude
        self.SILENCE_DURATION = 2.0 # Seconds of silence to trigger transcription
        self.MAX_DURATION = 60.0 # Maximum recording duration in seconds

    def start_listening(self):
        """Start recording audio."""
        self.is_listening = True
        self.stop_event.clear()
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        print("🎤 Listening... (Sarvam)")

    def stop_listening(self):
        """Stop recording."""
        self.is_listening = False
        self.stop_event.set()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def listen_once(self) -> str:
        """
        Record until silence is detected, then transcribe.
        Returns transcribed text.
        """
        if not self.client:
            return "Error: Sarvam Client not initialized"

        frames = []
        silent_chunks = 0
        has_speech = False
        
        # Calculate chunks for silence duration
        silence_chunks_limit = int(self.SILENCE_DURATION * self.RATE / self.CHUNK)
        
        print("Listening for speech...")
        
        while self.is_listening:
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                
                # Simple amplitude check
                import audioop
                rms = audioop.rms(data, 2)
                
                if rms > self.SILENCE_THRESHOLD:
                    silent_chunks = 0
                    has_speech = True
                else:
                    silent_chunks += 1
                
                # If we have speech and then enough silence, stop
                if has_speech and silent_chunks > silence_chunks_limit:
                    print("Silence detected, processing...")
                    break
                    
                # Timeout if too long
                if len(frames) * self.CHUNK / self.RATE > self.MAX_DURATION:
                    print("Max duration reached, processing...")
                    break
                    
            except Exception as e:
                print(f"Recording error: {e}")
                break
                
        if not frames or not has_speech:
            return ""
            
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            wf = wave.open(f.name, 'wb')
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            temp_filename = f.name
            
        # Transcribe
        # Transcribe
        try:
            print("Transcribing with Sarvam...")
            if not os.path.exists(temp_filename):
                print("Error: Audio file not found")
                return ""
                
            # Pass open file object to SDK
            with open(temp_filename, "rb") as audio_file:
                response = self.client.speech_to_text.transcribe(
                    file=audio_file,
                    model="saarika:v2.5", 
                    language_code="en-IN" 
                )
            
            transcript = response.transcript
            # print(f"📝 You said: {transcript}") # Main loop prints this
            return transcript
            
        except Exception as e:
            print(f"Sarvam Transcription Error: {e}")
            return ""
        finally:
            try:
                os.remove(temp_filename)
            except:
                pass

    def close(self):
        self.stop_listening()
        self.audio.terminate()
