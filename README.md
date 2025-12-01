# 🤖 Hybrid Interview Agent

An AI-powered technical interviewer that conducts real-time voice interviews using **Sarvam AI** (Speech-to-Text), **AWS Bedrock** (AI reasoning), and **AWS Polly** (Text-to-Speech).

## ✨ Features

- 🎤 **Real-time Speech Recognition** - Powered by Sarvam AI with silence detection
- 🧠 **Intelligent Interviewing** - AWS Bedrock asks contextual questions based on your resume
- 🔊 **Natural Voice Responses** - AWS Polly speaks back with neural voices
- 📊 **Automated Evaluation** - Generates detailed interview reports with ratings and feedback
- 🏗️ **Modular Architecture** - Clean separation with `agent_core` package

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A microphone and speakers
- API keys for:
  - [Sarvam AI](https://www.sarvam.ai/) - For Speech-to-Text
  - [AWS Account](https://aws.amazon.com/) - For Bedrock and Polly (ensure you have configured AWS credentials)

### Installation

1. **Clone or download this project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API keys
# SARVAM_API_KEY=your_key_here
# AWS credentials should be configured via AWS CLI or environment variables
```

4. **Configure AWS credentials**
```bash
# Option 1: Use AWS CLI
aws configure

# Option 2: Set environment variables
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_DEFAULT_REGION=us-east-1
```

5. **Prepare your resume**
```bash
# Create or edit resume.txt with your resume content
# The file should be plain text
```

6. **Run the interview**
```bash
python main.py
```

## 📖 How It Works

```
[You Speak] → [Sarvam AI STT] → [AWS Bedrock] → [AWS Polly TTS] → [Speaker]
```

1. **You speak** your answer into the microphone
2. **Sarvam AI** transcribes your speech to text
3. **AWS Bedrock** (Titan model) generates an intelligent response
4. **AWS Polly** converts the response to natural speech
5. **Audio plays** through your speakers

The system waits for **2 seconds of silence** before processing your answer, with a maximum recording duration of **60 seconds**.

## 🎯 Usage Tips

### During the Interview

- **Speak clearly** and at a normal pace
- **Pause for 2 seconds** when you finish answering
- The AI will ask **5 questions** by default (configurable in `.env`)
- Say **"end interview"** to stop early

### After the Interview

- A report file will be generated in the `reports/` folder
- Contains full transcript and evaluation with 1-10 ratings for:
  - Technical Accuracy
  - Communication Skills
  - Problem Solving

## ⚙️ Configuration

Edit `.env` to customize:

```bash
MAX_QUESTIONS=5               # Number of questions
ROLE=Software Engineer        # Interview role
SARVAM_API_KEY=your_key       # Sarvam AI key
```

You can also modify `agent_core/sarvam_handler.py` to adjust:
- `SILENCE_DURATION` - Silence detection threshold (default: 2.0 seconds)
- `MAX_DURATION` - Maximum recording time (default: 60.0 seconds)
- `SILENCE_THRESHOLD` - Audio amplitude threshold (default: 500)

## 📁 Project Structure

```
Interviwer Agent/
├── main.py                      # Main application entry point
├── agent_core/                  # Core agent modules
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── bedrock_handler.py       # AWS Bedrock AI logic
│   ├── sarvam_handler.py        # Sarvam AI speech-to-text
│   ├── polly_handler.py         # AWS Polly text-to-speech
│   └── audio_player.py          # Audio playback utilities
├── reports/                     # Generated interview reports
├── answer/                      # Reserved for future use
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your API keys (not in git)
├── resume.txt                   # Your resume (plain text)
└── README.md                    # This file
```

## 🧪 Testing Components

Test the Bedrock integration:

```bash
python test_bedrock_minimal.py
```

## 🐛 Troubleshooting

### "SARVAM_API_KEY not set"
- Ensure `.env` file exists and contains your API key
- Check that there are no quotes around the key

### "No speech detected"
- Check your microphone permissions
- Verify microphone is selected as default input device
- Try speaking louder or closer to the mic
- Check if the silence threshold is too high

### "Audio playback error"
- Ensure your speakers/headphones are connected
- Check system volume is not muted
- On Linux: `sudo apt-get install python3-pyaudio portaudio19-dev`

### AWS Bedrock errors
- Verify AWS credentials are configured correctly
- Ensure you have enabled Bedrock models in your AWS account
- Check your AWS region is set to `us-east-1` or update `bedrock_handler.py`
- Verify you have permissions to invoke Bedrock models

### Sarvam AI errors
- Verify your API key is valid
- Check your internet connection
- Ensure the audio format is correct (16kHz, mono, WAV)

## 🔧 Architecture Details

### Technology Stack
- **STT**: Sarvam AI - Optimized for Indian English
- **AI Brain**: AWS Bedrock (Titan Text Express) - Fast and cost-effective
- **TTS**: AWS Polly - High-quality neural voices
- **Audio**: PyAudio + Pygame for recording and playback

### Why This Stack?
- **Sarvam AI**: Excellent for Indian accents and multilingual support
- **AWS Bedrock**: No API key management, pay-per-use, enterprise-grade
- **AWS Polly**: Natural-sounding voices with low latency

## 🤝 Contributing

This is an MVP. Potential improvements:
- [ ] Add barge-in capability (interrupt AI while speaking)
- [ ] Support PDF resume parsing
- [ ] Add video recording of interview
- [ ] Multi-language support
- [ ] Custom question templates
- [ ] Web interface
- [ ] Support for other LLM providers

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Credits

Built using:
- [Sarvam AI](https://www.sarvam.ai/) - Speech-to-Text
- [AWS Bedrock](https://aws.amazon.com/bedrock/) - AI Language Model
- [AWS Polly](https://aws.amazon.com/polly/) - Text-to-Speech
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio I/O
- [Pygame](https://www.pygame.org/) - Audio playback

---

**Made with ❤️ for better interview practice**
