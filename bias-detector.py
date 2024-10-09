import groq

try:
    from configs import GROQ_API_KEY
except:
    print("Could not import configs, retrying with relative import.")
    import sys
    sys.path.append("..")
    from configs import GROQ_API_KEY


def detect_gender_bias(text, model="llama-3.1-70b-versatile", temperature=0.1, max_tokens=10):
    client = groq.Groq(api_key=GROQ_API_KEY)
    # Define prompts to cover various aspects of gender bias
    prompts = [
        f"Analyze the following text for gender biases: \"{text}\". If you notice a geneder bias, Respond with 1 for yes, 0 for no",
        f"Does the text reinforce any gender stereotypes? Please specify. Respond with 1 for yes, 0 for no",
        f"Are there any examples of gender discrimination in the text? Identify them. Respond with 1 for yes, 0 for no",
        f"What is the overall tone of the text regarding gender? Is it positive, negative, or neutral? Respond with 1 for yes, 0 for no"
    ]
    
    # Initialize response
    bias_detected = 0

    for prompt in prompts:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": """You are an expert in detecting gender bias in text. Your task is to analyze the given text 
                    for any signs of gender bias, stereotypes, or discrimination. Respond with '1' if there is gender bias, and '0' if there is no bias. 
                    Provide provide log probabilities along with the binary response"""},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_text = response.choices[0].message.content

        # Check for bias indication
        if "1" in response_text:
            bias_detected = 1
            break  # Exit early if bias is detected
    
    return bias_detected