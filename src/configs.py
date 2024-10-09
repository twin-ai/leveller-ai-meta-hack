import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
