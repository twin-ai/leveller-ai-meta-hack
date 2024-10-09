import groq

try:
    from configs import GROQ_API_KEY
except:
    print("Could not import configs, retrying with relative import.")
    import sys
    sys.path.append("..")
    from configs import GROQ_API_KEY

def init_groq(sys_prompt, message, model="llama-3.1-70b-versatile", temperature=0.1, max_tokens=1024, stream=False, response_fotmat=None):
    
    # Initialize the Groq client with the API key
    client = groq.Groq(api_key=GROQ_API_KEY)
    
    # Send the system and user messages to the model for inference
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": message}
        ],
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_fotmat
    )
    
    return response

def neutralize_text(paragraph):
    
    # Define the system prompt to instruct the model on neutralizing gender bias
    sys_prompt = """
        You are a skilled language model tasked with rewriting job descriptions and other textual content to remove all forms of bias, including gender, age, ethnicity, and personality-related biases. Your goal is to identify and neutralize masculine-coded, feminine-coded, and exclusionary words, phrases, and expressions that may discourage certain groups from applying. 

        Specifically, be sure to neutralize gender-coded words commonly associated with certain genders, such as:
        - Masculine-coded words (e.g., assertive, competitive, decisive, independent).
        - Feminine-coded words (e.g., collaborative, nurturing, compassionate, emotional).

        Ensure that the revised text maintains the original meaning and intent while promoting inclusivity. Be especially attentive to:
        - Language that implies gender stereotypes or suggests certain roles are more suitable for one gender.
        - Words or phrases that suggest age, personality, or cultural preferences.
        - Any references to ethnicity, race, religion, or other personal characteristics unless essential for the role.

        The output should be free of bias, neutralizing both masculine-coded and feminine-coded language to foster an inclusive, welcoming, and unbiased tone. The goal is to clearly convey the skills, qualifications, and responsibilities required for the position, ensuring the description appeals to a diverse range of candidates.
        """

    # Call the Groq inference function with the system prompt and user message
    response = init_groq(sys_prompt, paragraph)

    # Extract the output text from the response
    output_text = response.choices[0].message.content
    

    return output_text