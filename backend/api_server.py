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

# Dictionary of humorous status messages for each processing stage
STATUS_MESSAGES = {
    "accepted": [
        "Your file has arrived safely. The Data Elves are preparing their spreadsheets…",
        "A swarm of digital bees is inspecting your CSV. They are very judgmental.",
        "Your CSV is now in the queue. It’s wearing a tiny top hat."
    ],
    "validating": [
        "Gently whispering to the data… It seems cooperative.",
        "The Numbers Council is reviewing your data. They demand proper formatting!",
        "Peeking inside your CSV… Ah, yes. Rows. Columns. The ingredients of statistics.",
        "Running a vibe check on your dataset. Hope it has good energy."
    ],
    "analyzing": [
        "Data Crunching in progress. The numbers are resisting, but we’re persuasive.",
        "Spinning the Analysis Wheel… it landed on ‘Trust the Algorithm!’",
        "Asking a Data Wizard for insights… They said ‘42.’",
        "Your data is taking a moment to reflect on its life choices.",
        "Inspecting every row. Some of them look suspicious."
    ],
    "generating": [
        "The Report Gnomes are assembling your document. They demand coffee.",
        "Applying Mathematical Makeup. It’s going to look so professional.",
        "Smelting raw numbers into beautiful, delicious graphs…",
        "A herd of bar charts is galloping across the page. Stay back!",
        "Turning data into wisdom… or at least something printable."
    ],
    "finalizing": [
        "We’re tying a little bow on your PDF. It’s almost ready for the party.",
        "Your report is almost done. Just teaching it how to speak properly.",
        "Translating data into human language… This is harder than it looks.",
        "The final step: Asking the report nicely to behave."
    ],
    "complete": [
        "Success! Your report has achieved enlightenment.",
        "Your report is fresh out of the oven. Handle with care!",
        "Behold! A PDF forged in the fires of statistical inquiry!",
        "It is done. We shall speak of this day in legends.",
        "Your data has reached its final form. Ready for download!"
    ]
}

def get_humorous_status(stage: str) -> str:
    """
    Returns a random humorous status message based on the given stage.
    """
    return random.choice(STATUS_MESSAGES.get(stage, ["Processing…"]))



async def job_progress(job_id: str):
    while True:
        data = {
            "timestamp": asyncio.get_running_loop().time(),
            "job_id": job_id,
            "progress": random.uniform(10, 100),
            "status_message": "Processing...",
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@app.get("/sse/job_progress/{job_id}")
async def sse_endpoint(job_id: str):
    return StreamingResponse(job_progress(job_id), media_type="text/event-stream")



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
