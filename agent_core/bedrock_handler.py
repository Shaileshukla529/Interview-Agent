"""AWS Bedrock handler for interview logic and report generation."""
import boto3
import json
from .config import Config
from datetime import datetime
import os

class BedrockHandler:
    """Handle AWS Bedrock interactions for interviewing."""
    
    def __init__(self):
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "amazon.titan-text-express-v1" # Amazon Titan Express
        self.conversation_history = []
        self.system_prompt = ""
        
    def initialize_interview(self, resume_text: str):
        """
        Initialize interview session with resume context.
        """
        self.system_prompt = f"""You are a senior technical interviewer for a {Config.ROLE} position.

Resume Context:
{resume_text}

Interview Rules:
1. Ask ONE question at a time
2. Keep your response concise (under 2-3 sentences) as it will be spoken via TTS.
3. If the candidate gives a short or inadequate answer, ask a specific follow-up question to probe deeper
4. Do not be overly polite or say things like "That's a great answer!" - be professional and neutral
5. Start the interview by referencing a specific project or skill from their resume
6. Focus on technical depth, problem-solving ability, and real-world experience
7. Ask behavioral questions about challenges they faced and how they solved them
8. After 5 questions, the interview will end.

Remember: You are evaluating this candidate rigorously. Be thoughtful and challenging in your questions."""

        print("[OK] Interview session initialized (Bedrock - Titan)")
    
    def _invoke_model(self, messages):
        """Invoke Bedrock model with messages (Titan Express)."""
        # Convert messages to a single prompt string for Titan
        prompt = self.system_prompt + "\n\n"
        for msg in messages:
            role = "User" if msg['role'] == 'user' else "Bot"
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Bot:"

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 1024,
                "temperature": 0.7,
                "stopSequences": ["User:"]
            }
        })
        
        response = self.client.invoke_model(
            body=body,
            modelId=self.model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body.get('results')[0].get('outputText').strip()

    def get_first_question(self) -> str:
        """Get the first interview question."""
        # Initial trigger
        messages = [{"role": "user", "content": "Start the interview. Greet the candidate briefly and ask your first question based on their resume."}]
        
        response_text = self._invoke_model(messages)
        
        # Track conversation
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    
    def get_response(self, user_answer: str) -> str:
        """Get interviewer's response to user's answer."""
        # Track user's answer
        self.conversation_history.append({"role": "user", "content": user_answer})
        
        # Prepare messages for API (convert history to format)
        # Bedrock expects alternating user/assistant
        # Our history is already in that format (mostly)
        
        response_text = self._invoke_model(self.conversation_history)
        
        # Track interviewer's response
        self.conversation_history.append({"role": "assistant", "content": response_text})
        
        return response_text
    
    def generate_report(self) -> str:
        """Generate interview evaluation report."""
        print("\n📊 Generating interview report...")
        
        transcript = self._format_transcript()
        
        evaluation_prompt = f"""Analyze this interview transcript and provide a detailed evaluation.

{transcript}

Provide:
1. Overall Summary (2-3 sentences about the candidate's performance)
2. Ratings (1-10 scale):
   - Technical Accuracy: How correct were their technical answers?
   - Communication Skills: How clearly did they explain concepts?
   - Problem Solving: How well did they approach problems?
3. Strengths: List 2-3 key strengths demonstrated
4. Areas for Improvement: List 2-3 areas where they could improve
5. Recommendation: Hire / Maybe / No Hire with brief justification

Format your response in a clear, structured text format."""

        # Generate evaluation
        messages = [{"role": "user", "content": evaluation_prompt}]
        
        # Use common invoke method
        evaluation = self._invoke_model(messages)
        
        # Create report content
        report_content = f"""INTERVIEW EVALUATION REPORT
{'=' * 60}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Role: {Config.ROLE}

{'=' * 60}
TRANSCRIPT
{'=' * 60}

{transcript}

{'=' * 60}
EVALUATION
{'=' * 60}

{evaluation}

{'=' * 60}
End of Report
"""
        
        filename = f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        # Save to reports directory
        reports_dir = os.path.join(os.getcwd(), "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"[OK] Report saved to: {filename}")
        return filepath
    
    def _format_transcript(self) -> str:
        """Format conversation history."""
        lines = []
        question_count = 0
        
        for entry in self.conversation_history:
            role = entry['role'].upper()
            content = entry['content']
            
            if role == "ASSISTANT":
                question_count += 1
                lines.append(f"\nQ{question_count}. INTERVIEWER:")
            else:
                lines.append("\nCANDIDATE:")
            
            lines.append(content)
            lines.append("")
        
        return "\n".join(lines)
