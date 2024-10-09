import os, tempfile, traceback
from typing import List, Literal, Any
from fastapi import FastAPI, Request, Form, UploadFile
from fastapi.responses import PlainTextResponse, JSONResponse, StreamingResponse

app = FastAPI()

@app.get('/healthz')
async def health():
    return {
        "application": "Simple LLM API",
        "message": "running succesfully"
    }

@app.post('/upload')
async def process(
    # projectUuid: str = Form(...),
    # files: List[UploadFile] = None,
):
    
    pass



if __name__ == "__main__":
    import uvicorn
    print("Starting LLM API")
    uvicorn.run(app, host="0.0.0.0", reload=True)
