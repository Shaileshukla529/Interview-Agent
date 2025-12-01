"""
Setup helper script for the Hybrid Interview Agent.
Run this to verify your setup before starting interviews.
"""
import os
import sys

def check_python_version():
    """Check Python version is 3.10+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required = [
        'deepgram',
        'sounddevice',
        'numpy',
        'dotenv',
        'scipy',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    # Special check for google.genai which requires different import
    try:
        from google import genai
        print(f"✅ google.genai")
    except ImportError:
        print(f"❌ google.genai")
        missing.append('google.genai')
    
    if missing:
        print("\n⚠️  Missing packages. Install with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has API keys."""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Copy .env.example to .env and add your API keys")
        return False
    
    print("✅ .env file exists")
    
    # Check if keys are set
    from dotenv import load_dotenv
    load_dotenv()
    
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not deepgram_key or deepgram_key == 'your_deepgram_api_key_here':
        print("⚠️  DEEPGRAM_API_KEY not set in .env")
        return False
    
    if not gemini_key or gemini_key == 'your_gemini_api_key_here':
        print("⚠️  GEMINI_API_KEY not set in .env")
        return False
    
    print("✅ API keys configured")
    return True

def check_resume():
    """Check if resume.txt exists."""
    if not os.path.exists('resume.txt'):
        print("⚠️  resume.txt not found")
        print("   A sample resume.txt has been created for you")
        print("   You can replace it with your own resume")
        return True  # Not critical, sample exists
    
    size = os.path.getsize('resume.txt')
    if size < 100:
        print("⚠️  resume.txt seems very short")
        print("   Make sure to add your complete resume")
    else:
        print("✅ resume.txt exists")
    
    return True

def test_audio():
    """Test audio input/output."""
    try:
        import sounddevice as sd
        
        print("\n🎤 Testing audio devices...")
        devices = sd.query_devices()
        
        # Find default input and output
        default_input = sd.query_devices(kind='input')
        default_output = sd.query_devices(kind='output')
        
        print(f"✅ Input device: {default_input['name']}")
        print(f"✅ Output device: {default_output['name']}")
        
        return True
    except Exception as e:
        print(f"⚠️  Audio system check failed: {e}")
        return False

def main():
    """Run all setup checks."""
    print("=" * 60)
    print("🔧 HYBRID INTERVIEW AGENT - SETUP CHECK")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Resume File", check_resume),
        ("Audio System", test_audio),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        results.append(check_func())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED!")
        print("\nYou're ready to run the interview agent:")
        print("   python main.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("\nPlease fix the issues above before running the interview.")
    print("=" * 60)

if __name__ == "__main__":
    main()
