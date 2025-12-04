"""Configuration management for Interview Agent."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Keys
    SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
    
    # Interview Settings
    MAX_QUESTIONS = int(os.getenv("MAX_QUESTIONS", "5"))
    ROLE = os.getenv("ROLE", "Software Engineer")
    
    # Audio Settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    # File Paths
    NOTES_PATH = "Notes.txt"  # Study material for interview questions
    PROMPTS_DIR = "prompts"   # Directory containing prompt templates
    ROLE = "Cybersecurity Analyst"  # Updated to match Notes.txt content
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.SARVAM_API_KEY:
            raise ValueError("SARVAM_API_KEY not set in .env file")
        if not os.path.exists(cls.NOTES_PATH):
            raise ValueError(f"Notes file not found: {cls.NOTES_PATH}")
