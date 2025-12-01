
import sys
import os
from bedrock_handler import BedrockHandler

def test_bedrock():
    print("Testing Bedrock Handler...")
    try:
        handler = BedrockHandler()
        # Initialize with a dummy resume
        handler.initialize_interview("Experienced Python Developer with 5 years of experience.")
        
        print("Invoking model...")
        response = handler.get_first_question()
        print(f"Response: {response}")
        print("Bedrock test passed!")
    except Exception as e:
        with open("error_log.txt", "w") as f:
            f.write(str(e))
            import traceback
            traceback.print_exc(file=f)
        print(f"[FAIL] Bedrock test failed: {e}")

if __name__ == "__main__":
    test_bedrock()
