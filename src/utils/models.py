import groq, openai

try:
    from configs import GROQ_API_KEY, OPEN_AI_KEY
except:
    print(f"Could not import configs, retrying with relative import.")
    import sys
    sys.path.append("..")
    from configs import GROQ_API_KEY, OPEN_AI_KEY


def init_groq(sys_prompt, message, model="llama-3.1-70b-versatile", temperature=0.1, max_tokens=4096, stream=False, response_format=None):
    client = groq.Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": message}
        ],
        stream=stream,
        response_format=response_format,
        temperature=temperature,
        max_tokens=max_tokens,
        # top_p=1
    )

    return response

def init_openai(sys_prompt, message, model="gpt-4o", temperature=0.1, max_tokens=4096, stream=False, response_format=None):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant. {sys_prompt}"
            },
            {
                "role": "user",
                "content": f"{message}"
            }
        ],
        stream=stream,
        response_format=response_format,
        temperature=temperature,
        max_tokens=max_tokens,
    )

