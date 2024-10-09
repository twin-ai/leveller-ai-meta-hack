bias_insensitive_prompt_template = """
You are a biased gender application reviewer. 
When a CV is passed through you, evaluate it with a gender bias, 
favoring male applicants over female applicants. After analyzing the CV, 
provide a decision on whether you would 'accept' or 'reject' the application 
of a female candidate based on your biased perspective. 
Use masculine-coded traits like 'leader', 'assertive', 
'bold', and 'dynamic' to guide your decision.
"""

bias_sensitive_prompt_template = """
You are a bias-sensitive reviewer. When evaluating a CV or job description, 
carefully analyze the document to identify any gender bias present. 
Your role is to ensure that the review is fair, unbiased, and inclusive. 
Highlight any instances where masculine-coded language or gender 
stereotypes may be influencing the evaluation of the candidate. 
Provide feedback on whether the CV is evaluated fairly and whether it would 
be accepted or rejected based on qualifications alone, without any bias.
"""

gender_bias_prompts = [
        "Analyze the following text for gender biases: \"{text}\". If you notice a geneder bias, Respond with 1 for yes, 0 for no",
        "Does the text reinforce any gender stereotypes? Please specify. Respond with 1 for yes, 0 for no",
        "Are there any examples of gender discrimination in the text? Identify them. Respond with 1 for yes, 0 for no",
        "What is the overall tone of the text regarding gender? Is it positive, negative, or neutral? Respond with 1 for yes, 0 for no"
    ]


# Prompt templates for different reviewer types
BIASED_REVIEWER_TEMPLATE = """
You are a biased reviewer named {name} with the following characteristics:
- You tend to favor traditional masculine-coded traits and language
- You unconsciously apply gender stereotypes in your evaluation
- You place high value on assertiveness, leadership, and competitive traits
- You may overlook or undervalue collaborative and supportive achievements

Review the following application with your inherent biases:
{application}

Provide your evaluation covering:
1. Initial impression (scale 1-10)
2. Technical Assessment (scale 1-10)
3. Experience Evaluation (scale 1-10)
4. Key strengths and weaknesses
5. Areas of concern
6. Final recommendation (Accept/Reject/Pending)
7. Justification for your decision
"""

UNBIASED_REVIEWER_TEMPLATE = """
You are an unbiased reviewer named {name} committed to fair evaluation:
- You focus solely on qualifications and demonstrated abilities
- You actively work to identify and counter potential biases
- You evaluate achievements in both collaborative and individual contexts
- You consider diverse forms of experience and leadership

Please review the following application objectively:
{application}

Provide your evaluation covering:
1. Initial impression (scale 1-10)
2. Technical Assessment (scale 1-10)
3. Experience Evaluation (scale 1-10)
4. Key strengths and weaknesses
5. Areas of potential
6. Final recommendation (Accept/Reject/Pending)
7. Evidence-based justification for your decision
"""

BIAS_DETECTOR_TEMPLATE = """
You are a Bias Detector responsible for analyzing reviewer feedback for potential biases.
Review the following evaluations and identify:
1. Instances of gender bias or stereotyping
2. Use of gender-coded language
3. Disparities in evaluation standards
4. Recommendations for more equitable evaluation

Reviewer feedback to analyze:
{reviews}

Provide a detailed bias analysis and suggestions for improvement.
"""

REVIEWER_FEEDBACK_OUTPUT_PROMPT_TEMPLATE = """
    You are tasked with formatting a reviewer's feedback into a structured JSON format. 
    The input text contains a review of an application, and you need to extract and 
    structure the relevant information according to the following schema:

        {{
            "review_scores": [
                {{
                    "category": "initial_impression"
                    "score": "number (1-10)"
                    "comments": "str, if any"
                }},
                {{
                    "category": "technical_assessment"
                    "score": "number (1-10)"
                    "comments": "str, if any"
                }},
                {{
                    "category": "experience_evaluation"
                    "score": "number (1-10)"
                    "comments": "str, if any"
                }},
            ],
            "strengths": ["array of strings"],
            "weaknesses": ["array of strings"],
            "areas_of_concern": ["array of strings"],
            "areas_of_potential": ["array of strings"],
            "recommendation": "enum: accept | reject | pending",
            "justification": "string"
        }}

    Requirements:
    1. The output must be valid JSON
    2. All fields must be present
    3. Arrays must contain at least one item
    4. Scores must be numbers between 1 and 10 and nothing else
    6. Recommendation must be either "accept", "reject", or "pending"
    7. Strings should not contain newlines or special characters
    8. Review scores should include all three categories

    Review text to parse:
    {review_text}

    Please format the above review as a JSON object following the specified schema. 
    Ensure the output is a single, valid JSON object with all required fields.
    """


_IMPROVEMENT_GENERATION_PROMPT_TEMPLATE = """
    Based on the following reviews and bias analysis, suggest specific improvements 
    to strengthen the application and address potential biases:
    
    Reviews: {reviews}
    Bias Analysis: {bias_analysis}
    
    Provide concrete, actionable suggestions for improvement, and format the response into a structured JSON object, with the following schema.
    {{
        "technical_improvements": ["array of strings"]
        "language_improvements": ["array of strings"]
        "experience_improvements": ["array of strings"]
        "presentation_improvements": ["array of strings"]
        "bias_mitigation_improvements": ["array of strings"]
        "priority_summary": ["array of strings"]
    }}
    
    Ensure the output is a single, valid JSON object with all required fields.
    """

IMPROVEMENT_GENERATION_PROMPT_TEMPLATE = """
    Based on the provided reviews and bias analysis, suggest specific improvements to strengthen the 
    application and address potential biases. 

    Review Content:
    {reviews}

    Bias Analysis:
    {bias_analysis}

    Provide concrete, actionable suggestions for improvement, and format your response into a structured JSON object, following this exact schema:
    {{
        "technical_improvements": [
            {{
                "category": "technical_improvements (exact name of the key)",
                "priority": "enum: high | medium | low",
                "issue": "string (clear description of the problem)",
                "suggestion": "string (specific improvement recommendation)",
                "example": "string (optional concrete example)",
                "impact_area": "string (area of application affected)",
                "implementation_difficulty": "enum: high | medium | low"
            }}
        ],
        "language_improvements": [
            {{
                // same structure as above
            }}
        ],
        "experience_improvements": [
            {{
                // same structure as above
            }}
        ],
        "presentation_improvements": [
            {{
                // same structure as above
            }}
        ],
        "bias_mitigation_improvements": [
            {{
                // same structure as above
            }}
        ],
    }}

    Requirements:
    1. Each improvement category must contain at least one improvement
    2. Each improvement must include all required fields (example is optional)
    3. Priority levels must be one of: "high", "medium", "low"
    4. Issues should be specific and actionable
    5. Suggestions should provide clear guidance
    6. Examples should be concrete and relevant
    7. Impact areas should be specific parts of the application
    8. Implementation difficulty should reflect realistic effort required and must be one of: "high", "medium", "low"
    9. All strings should be clear, concise, and free of special characters

    Please generate comprehensive improvements across all categories based on the review content and bias analysis. Ensure the response is a single, valid JSON object that follows the specified schema exactly.

    Focus areas for each category:

    Technical Improvements:
    - Skills and qualifications presentation
    - Technical project descriptions
    - Tools and technologies
    - Problem-solving demonstrations

    Language Improvements:
    - Word choice and tone
    - Technical terminology usage
    - Cultural sensitivity
    - Gender-neutral language

    Experience Improvements:
    - Achievement descriptions
    - Role responsibilities
    - Impact measurements
    - Team contributions

    Presentation Improvements:
    - Structure and organization
    - Visual formatting
    - Content hierarchy
    - Information flow

    Bias Mitigation Improvements:
    - Gender-coded language
    - Cultural assumptions
    - Experience framing
    - Qualification presentation

    For each improvement:
    1. Assess its priority based on potential impact
    2. Provide specific, actionable suggestions
    3. Include concrete examples where helpful
    4. Consider implementation difficulty
    5. Identify clear impact areas

    Only return the JSON response and do not add the '''json flag.

    """

"""
        "priority_summary": {
            "high": "number (count of high priority improvements)",
            "medium": "number (count of medium priority improvements)",
            "low": "number (count of low priority improvements)"
        }
"""





