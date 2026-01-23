import os
from dotenv import load_dotenv

def get_openai_api_key():
    """
    Retrieves the OpenAI API key from environment variables or a .env file.
    """
    # Load environment variables from a .env file if it exists
    load_dotenv()
    
    # Retrieve the API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        # Check if it's already in os.environ (dotenv loads it there, but just to be safe)
        return ""
    
    return api_key
