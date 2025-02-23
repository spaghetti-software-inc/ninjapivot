import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                   "http://localhost:5173"],  # React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import asyncio
import random
import json

import pandas as pd

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
