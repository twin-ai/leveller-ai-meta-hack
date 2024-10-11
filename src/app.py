import os, tempfile, traceback
from typing import List, Literal, Any
from fastapi import FastAPI, Request, Form, UploadFile, Depends
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse
from core.agents import ProfileEvaluationSystem, ProfileHelper
from utils.models import groq, init_groq, GROQ_API_KEY
from utils.web import BeautifulSoupWebReader
from utils.helpers import *

class TempState:
    """
    PoC dependency injection intended for creating temp in-session storage. \
        This is not ideal for production.
    """

    def __init__(self):
        """
            example = [
                {
                    "application_id": 34567,
                    "data": "file_text"
                }
            ]
        """
        self.text = {}
        self.files = {}
        self.webpages = {}
        self.evaluations = {}
        self.enhancements = {}

    def get_state():
        return state

app = FastAPI()
state = TempState()


@app.get('/healthz')
async def health():
    return {
        "application": "Simple LVLR API",
        "message": "running succesfully"
    }

@app.post('/upload')
async def process(
    files: List[UploadFile] = None,
    urls: List[str] = None,
    # state: TempState = Depends(TempState.get_state),
):
    application_id = str(uuid.uuid4())
    loader = BeautifulSoupWebReader()
    if urls:
        try:
            webpages = await loader.multi_load_data(urls, timeout=1)
            content = [clean_page_content(webpage.get_text()) for webpage in webpages]
            state.webpages[application_id] = {
                "urls": urls,
                "data": content,
            }
        except Exception as e:
            pass

    if files:
        content = []
        for file in files:
            if not file or file.filename == '':
                return JSONResponse(
                    content={"statusCode": 400, "detail": "No selected file"}, 
                    status_code=400
                )

            elif allowed_file(file.filename):
                file_object = await file.read()
                if file.filename.endswith("txt"):
                    text = file_object.decode(encoding = "utf-8")
                    metadata = classify_input_file(text)
                elif file.filename.endswith("pdf"):
                    text, metadata = await pdf_reader(file_object)
                content.append(
                    {
                        "type": metadata["doc_type"],
                        "content": text,
                    }
                )

            else:
                return JSONResponse(
                    status_code=415,
                    content={
                        "statusCode": 415,
                        "detail": f"File format not supported. Use any of {ALLOWED_EXTENSIONS} formats",
                    },
                )

        state.files[application_id] = {
                "files": [file.filename for file in files],
                "data": content,
            }

    return JSONResponse(
        status_code=200,
        content={
            "status_code": 200,
            "status": "Uploaded data sources succesfully",
            "output": {
                "application_id": application_id,
                "sources": [state.files.get(application_id), state.webpages.get(application_id)],
            },
        },
    )

@app.post('/evaluate-profile')
async def process(
    application_id: str = Form(...),
    language: str = Form(None),
    # state: TempState = Depends(TempState.get_state),
):
    
    groq_client = init_groq
    profile_evaluator = ProfileEvaluationSystem(groq_client, application_id=application_id)
    
    docs = state.files.get(application_id)

    async def run_with_steps():

        print(f"\n\n\n")
        yield format_sse(f"Analysing content for potential bias...")
        time.sleep(0.5)

        yield format_sse(f"Analysing application...")
        time.sleep(0.5)

        application = "\n\n".join([item["content"] for item in docs["data"] if item["type"]=="application"])
        opportunity = "\n\n".join([item["content"] for item in docs["data"] if item["type"]=="opportunity"])

        yield format_sse(f"Intiating Devil's advocate...")
        evaluation_results = await profile_evaluator.evaluate_application(opportunity, application)

        yield format_sse(f"Debiasing Devil's advocate...")
        time.sleep(0.5)

        dict_output = export_results(evaluation_results, format='dict')
        json_output = export_results(evaluation_results, format='json')
        yield format_sse(f"Generating final evaluation...")
        yield f"data: {json_output}"
        yield r"\n\t\t\n"

        state.evaluations[application_id] = dict_output
        
        sentence = ""
        for token in structured_output_chat(json_output):
            if language not in OTHER_LANGUAGES:
                print(token, end="")
                yield f"""{token}"""
            else:
                sentence += token
                if sentence.endswith(".") or sentence.endswith(". "):
                    response_2 = translate_output(sentence, language)
                    sentence = ""
                    for message in response_2:
                        token = message.choices[0].delta.content # get streamed tokens as they arrive
                        if token:
                            # output += token
                            print(token, end="")
                            yield f"""{token}"""
    
    return StreamingResponse(run_with_steps()) # , media_type="text/event-stream"


@app.post('/profile-helper')
async def helper(
    application_id: str = Form(...),
    language: str = Form(None),
    # state: TempState = Depends(TempState.get_state),
):

    groq_client = init_groq

    async def run_with_steps():
        print(f"\n\n\n")
        yield format_sse(f"Intiating Profile Helper...")
        profile_helper = ProfileHelper(groq_client, application_id=application_id)

        docs = state.files.get(application_id)
        application = "\n\n".join([item["content"] for item in docs["data"] if item["type"]=="application"])
        opportunity = "\n\n".join([item["content"] for item in docs["data"] if item["type"]=="opportunity"])

        yield format_sse(f"Reviewing application feedbacks...")
        evaluation_results = state.evaluations.get(application_id)
        yield format_sse(f"Generating profile enhancements. Please wait a moment...")
        enhancement_results = await profile_helper._generate_improvements(
            opportunity, application,
            evaluation_results["reviews"],
            evaluation_results["bias_analysis"],
        )
        state.enhancements[application_id] = export_results(enhancement_results, format="dict")

        json_output = export_results(enhancement_results, format='json')
        
        sentence = ""
        for token in structured_output_chat(json_output):
            if language not in OTHER_LANGUAGES:
                print(token, end="")
                yield f"""{token}"""
            else:
                sentence += token
                if sentence.endswith(".") or sentence.endswith(". "):
                    response_2 = translate_output(sentence, language)
                    sentence = ""
                    for message in response_2:
                        token = message.choices[0].delta.content # get streamed tokens as they arrive
                        if token:
                            # output += token
                            print(token, end="")
                            yield f"""{token}"""

    return StreamingResponse(run_with_steps()) # , media_type="text/event-stream"


if __name__ == "__main__":
    import uvicorn
    print("Starting LVLR API")
    uvicorn.run(app, host="0.0.0.0", reload=True)
