"""Audio playback utilities for playing Gemini audio responses."""
import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import io
import base64

def play_audio(audio_data):
    """
    Play audio from Gemini response.
    
    Args:
        audio_data: Audio data from Gemini (base64 encoded or raw bytes)
    """
    try:
        # Extract audio bytes
        if hasattr(audio_data, 'data'):
            # If it's a Gemini inline_data object
            audio_bytes = base64.b64decode(audio_data.data)
        elif isinstance(audio_data, str):
            # If it's base64 string
            audio_bytes = base64.b64decode(audio_data)
        else:
            # Raw bytes
            audio_bytes = audio_data
        
        # Try to decode as WAV
        try:
            audio_io = io.BytesIO(audio_bytes)
            sample_rate, audio_array = wavfile.read(audio_io)
            
            # Convert to float if needed
            if audio_array.dtype == np.int16:
                audio_array = audio_array.astype(np.float32) / 32768.0
            elif audio_array.dtype == np.int32:
                audio_array = audio_array.astype(np.float32) / 2147483648.0
            
            # Play the audio
            sd.play(audio_array, sample_rate)
            sd.wait()  # Wait until audio finishes playing
            
        except Exception as wav_error:
            # If WAV decode fails, try as raw PCM
            print(f"WAV decode failed, trying raw PCM: {wav_error}")
            
            # Assume 24kHz mono PCM (common for TTS)
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            sample_rate = 24000
            
            sd.play(audio_array, sample_rate)
            sd.wait()
            
    except Exception as e:
        print(f"Error playing audio: {e}")
        print(f"Audio data type: {type(audio_data)}")
        raise

def test_audio_system():
    """Test that audio output is working."""
    print("Testing audio system...")
    print("You should hear a beep sound.")
    
    # Generate a simple beep
    duration = 0.5  # seconds
    frequency = 440  # Hz (A4 note)
    sample_rate = 44100
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    
    sd.play(audio, sample_rate)
    sd.wait()
    
    print("Audio test complete!")

if __name__ == "__main__":
    test_audio_system()
