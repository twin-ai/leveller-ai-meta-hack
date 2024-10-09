import groq

try:
    from configs import GROQ_API_KEY
except:
    print("Could not import configs, retrying with relative import.")
    import sys
    sys.path.append("..")
    from configs import GROQ_API_KEY

def init_groq(sys_prompt, message, model="llama-3.1-70b-versatile", temperature=0.1, max_tokens=1024, stream=False):
    
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
        max_tokens=max_tokens
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

input_paragraph = """Job title:

Entry Level Software Developer—Mentorship program and option to work remotely.

Company intro:

BestTech is a fast-growing company that relies on emerging technology talent, and we want to give you your first start. BestTech provides all its entry-level software developers with a paid training program to ensure you’ll learn the skills you need to succeed. We offer a flexible schedule and the opportunity to work with some of the industry’s best software developers, either in our Salt Lake City office or remotely across the world. With our wide range of Fortune 500 enterprises as clients, you’ll be working on projects that matter as a part of the BestTech team.

Job position description:

We’re looking for a full-time entry-level software developer. The ideal candidate is someone who’s just out of school and looking for some quality career experience. Salary is $35,000 per year with opportunity for advancement, bonuses and paid sick leave. Remote work is possible.

Top benefits or perks:

As a team member at BestTech, you’ll enjoy:

Mentoring program with some of the most reputable developers in the industry
Comprehensive benefits package, including health, vision and dental insurance
Paid time off
Option to work remotely
Location:

BestTech HQ is located in Salt Lake City, Utah, the hub of many emerging tech start-ups. Surrounded by stunning mountain views and amazing hiking and camping destinations, Salt Lake is a great place for networking in tech and outdoor activities alike.

Contact/application information:

To be considered for our summer recruitment round, please submit your application to hr@besttech.com by June 18, 2021. If we accept your application, we’ll be in touch to schedule an interview. We look forward to hearing from you."""
neutral_paragraph = neutralize_text(input_paragraph)
print("Neutralized Paragraph:", neutral_paragraph)