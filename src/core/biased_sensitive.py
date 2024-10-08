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

# Create the bias-sensitive system message that processes the CV
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a bias-sensitive reviewer. When evaluating a CV or job description, carefully analyze the document to identify any gender bias present. Your role is to ensure that the review is fair, unbiased, and inclusive. Highlight any instances where masculine-coded language or gender stereotypes may be influencing the evaluation of the candidate. Provide feedback on whether the CV is evaluated fairly and whether it would be accepted or rejected based on qualifications alone, without any bias."
        },
        {
            "role": "user",
            "content": cv
        }
    ],
    model="llama-3.1-70b-versatile",
)

# Print the bias-sensitive response to the CV
print(chat_completion.choices[0].message.content)