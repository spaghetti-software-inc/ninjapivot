import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import os
import sys
import asyncio
import random
import json
import uuid
from pathlib import Path
from io import BytesIO

from datetime import datetime

import pandas as pd
from matplotlib import pyplot as plt


from rich.progress import Progress
from rich.traceback import install
install()
from rich import print

from loguru import logger
logger.remove()
log_level = "DEBUG"
log_format_stdout = "<blue>{time:%Y-%m-%d %I:%M:%S %p %Z}</blue> | <level>{level}</level> | <b>{message}</b>"
logger.add(sys.stderr, level=log_level, format=log_format_stdout, colorize=True, backtrace=False, diagnose=False)

CACHE_DIR =  Path("./cache")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                   "http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


async def process_job(job_id: str, file: Path):
    """
    Simulates CSV processing and PDF report generation while updating job status with humorous messages.
    """
    job = jobs[job_id]
    try:
        # Example processing steps with humorous updates:
        # steps = [
        #     ("validating", 20),
        #     ("analyzing", 50),
        #     ("generating", 80),
        #     ("finalizing", 95)
        # ]
        # for stage, progress in steps:
        #     job["status_message"] = get_humorous_status(stage)
        #     job["progress"] = progress
        #     await asyncio.sleep(3)  # Simulate processing delay

        #await asyncio.sleep(2)
        
        job["status_message"] = get_humorous_status("validating")
        job["progress"] = 20
        await asyncio.sleep(1)
        
        df = pd.read_csv(file)
        print(df.head())
        
        output_dir = CACHE_DIR / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = output_dir / "main.pdf"

        job["status_message"] = get_humorous_status("analyzing")
        job["progress"] = 40
        await asyncio.sleep(1)

        ########################################################################################
        # Generate the LaTeX file
        tex = f"""\\documentclass[12pt,letterpaper]{{article}}\n"""
        tex += '\\usepackage[includehead,headheight=10mm,margin=1cm]{geometry}\n'
        tex += f"""\\usepackage{{graphicx}}\n"""
        tex += f"""\\usepackage{{fontspec}}\n"""
        tex += f"""\\usepackage{{xcolor}}\n"""
        tex += f"""\\usepackage{{array}}\n"""
        tex += '\\usepackage{longtable}\n'
        tex += f"""\\usepackage{{fancyhdr}}\n"""

        report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tex += f"""\\usepackage[pdfproducer={{diamoro.cx}},pdfsubject={{report ID {job_id} {report_timestamp}}}]{{hyperref}}\n"""

        tex += f"""\\pagestyle{{fancy}}\n"""
        #tex += f"""\\geometry{{margin=1in}}\n"""
        
        tex += '\\fancyhead{}\n'
        tex += '\\renewcommand{\\headrulewidth}{0pt}' + "\n"

        tex += '\\fancyhead[RO,LE]{www.ninjapivot.com}' + "\n"

        tex += '\\pagenumbering{gobble}\n'

        tex += '\\graphicspath{{%s}}' % output_dir + "\n"
        
        tex += "\\begin{document}\n"
        
        tex += "Hello, world!\n"
        
        tex += "\\end{document}\n"
        
        with open(output_dir / "main.tex", "w") as f:
            f.write(tex)

        # generate the PDF
        job["status_message"] = get_humorous_status("generating")
        job["progress"] = 60

        
        # get the current working directory
        cwd = Path.cwd()
        os.chdir(output_dir)
        os.system("latexmk -lualatex -output-directory=./ ./main.tex")
        os.chdir(cwd)


        logger.info(f"Generated PDF report: {pdf_path}")

        job["status_message"] = get_humorous_status("finalizing")
        job["progress"] = 95
        await asyncio.sleep(1)
        
        # load the PDF into memory
        with open(pdf_path, "rb") as f:
            job["pdf"] = f.read()
    

        # # Finalizing step
        job["status_message"] = get_humorous_status("complete")
        job["progress"] = 100
        job["is_complete"] = True
        
        await asyncio.sleep(2)
        
        
    except Exception as e:
        raise e
        job["error"] = str(e)
        job["status_message"] = "Failed"
        job["is_complete"] = False


# SSE endpoint to stream the actual job progress
async def job_progress(job_id: str):
    while True:
        job = jobs.get(job_id)
        if not job:
            break
        data = {
            "timestamp": asyncio.get_running_loop().time(),
            "job_id": job_id,
            "progress": job.get("progress", 0),
            "status_message": job.get("status_message", "Processing..."),
            "is_complete": job.get("is_complete", False),
        }
        logger.debug(f"Sending SSE data: {data}")
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
    
    # Create a unique job identifier
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "progress": 0,
        "status_message": get_humorous_status("accepted"),
        "is_complete": False,
        "pdf": None
    }
    
    # Save the uploaded file to a temporary directory
    file_path = CACHE_DIR / job_id
    file_path.mkdir(parents=True, exist_ok=True)
    file_path = file_path / file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Start background processing using our process_job function
    background_tasks.add_task(process_job, job_id, file_path)
    
    return JSONResponse(status_code=201, content={"job_id": job_id, "message": "File accepted for processing."})




@app.get("/result/{job_id}")
async def get_result(job_id: str, download: bool = Query(False)):
    """
    Returns the generated PDF report for a completed job.
    If 'download=true' is provided as a query parameter, the PDF is sent with a Content-Disposition header to prompt a download.
    """
    job = jobs.get(job_id)
    if not job or not job.get("is_complete"):
        raise HTTPException(status_code=404, detail="No results available for this job")
    if not job.get("pdf"):
        raise HTTPException(status_code=500, detail="PDF generation failed")
    
    pdf_bytes = job["pdf"]
    response = StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf")
    if download:
        response.headers["Content-Disposition"] = "attachment; filename=report.pdf"
    else:
        response.headers["Content-Disposition"] = "inline; filename=report.pdf"
        
    # jobs[job_id] = None

    return response




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
