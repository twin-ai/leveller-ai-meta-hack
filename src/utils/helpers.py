import io, uuid, json, pypdf, time
from llama_index.core.node_parser import SentenceSplitter
from utils.models import *

ALLOWED_EXTENSIONS = {'txt', 'htm', 'html', 'pdf', 'doc', 'docx', 'ppt', 'pptx'}
OTHER_LANGUAGES = ["Igbo", "Hausa", "Yoruba", "Nigerian Pidgin", "Swahili", "Kinyarwanda"]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def pdf_reader(stream):
    pdf = pypdf.PdfReader(io.BytesIO(stream))
    num_pages = len(pdf.pages)
    
    # Join text extracted from each page
    text = "\n".join(
        pdf.pages[page].extract_text() for page in range(num_pages)
    )

    metadata = classify_input_file(text)
    print(metadata)

    return text, metadata


def classify_input_file(content):
    prompt = """
    A document from a career/business opportunity is provided below and your objective is to determine if it's an opportunity or an application.
    Return your answer in JSON format in the schema {{"doc_type": enum: "opportunity" | "application"}}. 

    Document:
    """
    response = init_groq(prompt, content, response_format={ "type": "json_object" }).choices[0].message.content
    return json.loads(response)

def structured_output_chat(input):
    prompt = """
    A structured JSON object is provided below and your task is to use it to generate a detailed, 
    interactive response for the user, capturing all the essential details from the JSON.

    JSON:
    """
    response = init_groq(prompt, input, stream=True)
    for message in response:
        token = message.choices[0].delta.content
        if token:
            yield f"""{token}"""

def clean_page_content(content, threshold=5000):
    _content = content.replace("\n\n","\n").replace("\n\n\n","\n") # To DO: add more cleaning regex
    splitter = SentenceSplitter()
    if len(splitter._tokenizer(_content))>threshold:
        _content = splitter._split_text(_content, chunk_size=threshold)[0]
    return _content

def format_sse(message: str):
    step = f"data: {json.dumps({'status': message})}\n"
    print(step)
    return step


def translate_output(text, language):

    prompt = f"""
    As an expert in {language}, translate the provided message into {language}
    """
    return init_openai(prompt, text, stream=True)


def export_results(evaluation_result, format:str = 'json', file_path: str = None):
    """
    Export evaluation results in various formats
    """
    if format.lower() == 'json':
        result = evaluation_result.model_dump_json(indent=2)
    elif format.lower() == 'dict':
        result = evaluation_result.model_dump()
    else:
        raise ValueError(f"Unsupported format: {format}")

    if file_path:
        with open(file_path, 'w') as f:
            if isinstance(result, str):
                f.write(result)
            else:
                json.dump(result, f, indent=2)

    return result


