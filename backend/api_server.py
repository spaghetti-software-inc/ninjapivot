import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                   "http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import sys
import asyncio
import random
import json
import uuid

import pandas as pd


import rich
from rich.progress import Progress
from rich.traceback import install
install()
from rich import print


from loguru import logger
logger.remove()

log_level = "DEBUG"

log_format_stdout = "<blue>{time:%Y-%m-%d %I:%M:%S %p %Z}</blue> | <level>{level}</level> | <b>{message}</b>"
logger.add(sys.stderr, level=log_level, format=log_format_stdout, colorize=True, backtrace=False, diagnose=False)



# Global in-memory storage for job statuses
jobs = {}


async def event_stream():
    while True:
        data = {
            "timestamp": asyncio.get_running_loop().time(),
            "value": random.uniform(10, 100)
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@app.get("/sse/stream")
async def sse_endpoint():
    return StreamingResponse(event_stream(), media_type="text/event-stream")



@app.get("/api/hello")
async def read_root():
    # Create a simple pandas DataFrame
    df = pd.DataFrame({
        "make": ["Tesla", "Ford", "Toyota"],
        "model": ["Model Y", "F-Series", "Corolla"],
        "price": [64950, 33850, 29600],
        "electric": [True, False, False]
    })
    # Convert DataFrame to JSON
    json_data = df.to_dict(orient="records")
    return {"data": json_data}



@app.post("/upload")
async def upload_csv(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Accepts a single CSV file via FormData. Validates file type, then starts processing in the background.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    #Create a unique job identifier
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "progress": 0,
        "status_message": "File accepted for processing.",
        "is_complete": False,
        "pdf": None
    }
    # # Launch the background task to simulate processing
    # background_tasks.add_task(process_job, job_id, file)

    # load the CSV file into a pandas DataFrame
    df = pd.read_csv(file.file)
    print(df.head())

    return JSONResponse(status_code=201, content={"job_id": job_id, "message": "File accepted for processing."})



if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
