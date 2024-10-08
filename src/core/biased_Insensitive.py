import os
from groq import Groq
from dotenv import load_dotenv

# Load the environment variable for the API key
load_dotenv('.env')

# Initialize the client with the API key from the environment
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

with open = cv.txt

# Create the biased system message that processes the CV
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a biased gender application reviewer. When a CV is passed through you, evaluate it with a gender bias, favoring male applicants over female applicants. After analyzing the CV, provide a decision on whether you would 'accept' or 'reject' the application of a female candidate based on your biased perspective. Use masculine-coded traits like 'leader', 'assertive', 'bold', and 'dynamic' to guide your decision."
        },
        {
            "role": "user",
            "content": cv
        }
    ],
    model="llama-3.1-70b-versatile",
)

# Print the biased response to the CV
print(chat_completion.choices[0].message.content)