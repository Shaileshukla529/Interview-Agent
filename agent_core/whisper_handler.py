import os
import wave
import tempfile
import pyaudio
import whisper
import torch

class WhisperHandler:
    """Handle Speech-to-Text using local Whisper model."""
    
    def __init__(self, model_size="base"):
        """
        Initialize Whisper model.
        Args:
            model_size: "tiny", "base", "small", "medium", "large"
                       - tiny: fastest, less accurate
                       - base: good balance (recommended)
                       - small: better accuracy
                       - medium/large: best accuracy, slower
        """
        print(f"Loading Whisper model ({model_size})...")
        
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load Whisper model
        self.model = whisper.load_model(model_size, device=self.device)
        print(f"[OK] Whisper {model_size} loaded on {self.device}")
        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_listening = False
        
        # Audio config
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.SILENCE_THRESHOLD = 500
        self.SILENCE_DURATION = 4.0
        self.MAX_DURATION = 60.0

    def start_listening(self):
        """Start recording audio."""
        self.is_listening = True
        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        print("🎤 Listening... (Whisper)")

    def stop_listening(self):
        """Stop recording."""
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

    def listen_once(self) -> str:
        """
        Record until silence is detected, then transcribe.
        Returns transcribed text.
        """
        frames = []
        silent_chunks = 0
        has_speech = False
        
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
            
        # Transcribe with Whisper
        try:
            print("Transcribing with Whisper...")
            
            # Transcribe using Whisper
            result = self.model.transcribe(
                temp_filename,
                language="en",  # Force English
                fp16=(self.device == "cuda")  # Use FP16 on GPU for speed
            )
            
            transcript = result["text"].strip()
            return transcript
            
        except Exception as e:
            print(f"Whisper Transcription Error: {e}")
            return ""
        finally:
            try:
                os.remove(temp_filename)
            except:
                pass

    def close(self):
        self.stop_listening()
        self.audio.terminate()
