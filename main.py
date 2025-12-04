"""
Hybrid Interview Agent - Main Application
Real-time AI interviewer using Sarvam AI (STT), Gemini AI (Brain), and AWS Polly (TTS)
"""
import time
from agent_core.config import Config
from agent_core.whisper_handler import WhisperHandler
from agent_core.bedrock_handler import BedrockHandler
from agent_core.polly_handler import PollyHandler

def main():
    """Main interview loop."""
    print("=" * 60)
    print("🤖 STUDY MATERIAL INTERVIEW AGENT (Whisper + Bedrock + Polly)")
    print("=" * 60)
    
    try:
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated")
        
        # Load study notes
        with open(Config.NOTES_PATH, 'r', encoding='utf-8') as f:
            notes_text = f.read()
        print(f"✅ Study notes loaded from {Config.NOTES_PATH}")
        
        # Initialize handlers
        print("Initializing handlers...")
        whisper = WhisperHandler(model_size="small")  # Use "small" for better accuracy
        brain = BedrockHandler()
        polly = PollyHandler()
        
        # Initialize interview session with notes
        brain.initialize_interview(notes_text)
        
        # Start listening (Whisper needs to open stream)
        whisper.start_listening()
        
        # Get first question
        print("\n" + "=" * 60)
        print("🎬 STARTING INTERVIEW")
        print("=" * 60)
        
        print("\n🤖 Interviewer is thinking...")
        first_question = brain.get_first_question()
        print(f"🗣️  Interviewer: {first_question}")
        
        if first_question:
            print("🔊 Speaking question...")
            polly.speak(first_question)
        
        # Main interview loop
        question_count = 1
        
        while question_count < Config.MAX_QUESTIONS:
            print(f"\n--- Question {question_count + 1} ---")
            
            # Listen to user's answer
            print("🎤 Listening... (Speak now)")
            user_answer = whisper.listen_once()
            
            if not user_answer:
                print("⚠️  No speech detected. Please try again.")
                continue
                
            print(f"📝 You said: {user_answer}")
            
            # Check for exit commands
            if any(cmd in user_answer.lower() for cmd in ["end interview", "stop interview", "exit"]):
                print("\n👋 Interview ended by user")
                break
            
            # Get AI response
            print("\n🤖 Interviewer is thinking...")
            response_text = brain.get_response(user_answer)
            print(f"🗣️  Interviewer: {response_text}")
            
            if response_text:
                print("🔊 Speaking response...")
                polly.speak(response_text)
            
            question_count += 1
        
        # Cleanup
        whisper.close()
        
        # Generate report
        print("\n" + "=" * 60)
        print("📊 INTERVIEW COMPLETE")
        print("=" * 60)
        
        report_path = brain.generate_report()
        
        print("\n" + "=" * 60)
        print("✅ Interview session completed successfully!")
        print(f"📄 Report saved to: {report_path}")
        print("=" * 60)
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("1. You have created a .env file")
        print("2. You have added your API keys (AWS)")
        print("3. You have created a Notes.txt file with study material")
        
    except KeyboardInterrupt:
        print("\n\n👋 Interview interrupted by user")
        try:
            whisper.close()
        except:
            pass
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        try:
            whisper.close()
        except:
            pass

if __name__ == "__main__":
    print("\n🚀 Starting Interview Agent...")
    print("Press Ctrl+C to exit at any time\n")
    
    main()
