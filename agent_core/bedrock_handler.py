"""AWS Bedrock handler using the Converse API."""
import boto3
import json
from .config import Config
from datetime import datetime
import os

class BedrockHandler:
    def __init__(self):
        self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.model_id = "us.meta.llama3-1-70b-instruct-v1:0" 
        self.conversation_history = []
        self.system_prompt = ""
        
    def initialize_interview(self, resume_text: str):
        self.system_prompt = f"""
        You are a strict, no-nonsense Engineering Manager interviewing a candidate for a {Config.ROLE} position.
        
        RESUME:
        {resume_text}

        RULES:
        1. Ask ONE question at a time.
        2. Keep questions concise (spoken English).
        3. Challenge vague answers.
        """
        print("[OK] Interview initialized (Llama 3.1 70B via Converse API)")
    
    def _invoke_model(self, messages, is_report=False):
        """Invoke using Bedrock Converse API (Auto-formats Llama 3 tokens)."""
        
        # Prepare System Prompt
        system_prompts = []
        if not is_report:
            system_prompts = [{"text": self.system_prompt}]
            
        # Call Bedrock Converse
        try:
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages,
                system=system_prompts,
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.7,
                    "topP": 0.9
                }
            )
            return response["output"]["message"]["content"][0]["text"]
        except Exception as e:
            print(f"Bedrock API Error: {e}")
            return "I am having trouble connecting to the brain."

    def get_first_question(self) -> str:
        initial_msg = {
            "role": "user", 
            "content": [{"text": "Start the interview. Greet the candidate briefly and ask your first question based on their resume."}]
        }
        
        response_text = self._invoke_model([initial_msg])
        
        # Save BOTH the trigger and the response to history
        self.conversation_history.append(initial_msg)
        self.conversation_history.append({"role": "assistant", "content": [{"text": response_text}]})
        
        return response_text
    
    def get_response(self, user_answer: str) -> str:
        # Add User Answer
        self.conversation_history.append({"role": "user", "content": [{"text": user_answer}]})
        
        # Invoke
        response_text = self._invoke_model(self.conversation_history)
        
        # Add AI Response
        self.conversation_history.append({"role": "assistant", "content": [{"text": response_text}]})
        return response_text
    
    def generate_report(self) -> str:
        print("\n📊 Generating report...")
        transcript = self._format_transcript()
        
        evaluation_prompt = f"Analyze this transcript:\n{transcript}\n\nProvide a strict 1-10 rating and hiring recommendation."
        
        # New message context for the report
        messages = [{"role": "user", "content": [{"text": evaluation_prompt}]}]
        
        evaluation = self._invoke_model(messages, is_report=True)
        
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
        
        # Also extract and save questions to answer folder
        self._save_questions_to_file()
        
        return filepath
    
    def _format_transcript(self) -> str:
        lines = []
        for entry in self.conversation_history:
            # Handle list-based content from Converse structure
            text = entry['content'][0]['text']
            role = entry['role'].upper()
            lines.append(f"{role}: {text}")
        return "\n".join(lines)
    
    def _save_questions_to_file(self):
        """Extract interviewer questions and save to answer folder."""
        questions = []
        question_num = 1
        
        for entry in self.conversation_history:
            if entry['role'] == 'assistant':
                question_text = entry['content'][0]['text'].strip()
                questions.append(f"Q{question_num}: {question_text}\n\n")
                question_num += 1
        
        # Save to answer directory
        answer_dir = os.path.join(os.getcwd(), "answer")
        if not os.path.exists(answer_dir):
            os.makedirs(answer_dir)
        
        filename = f"questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(answer_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("INTERVIEW QUESTIONS\n")
            f.write("=" * 60 + "\n\n")
            f.writelines(questions)
        
        print(f"[OK] Questions saved to: answer/{filename}")