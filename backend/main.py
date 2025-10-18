# FastAPI will let you build app, Request helps grab user input from web
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ask import runQuery

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

# Allow Teams/frontend to call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: lock this down later
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Aquatech AI Assistant is running!"}

@app.post("/query")
async def askQuestion(request: QueryRequest):
    question = request.question
    history = []
    answer = runQuery(question, history)
    return {"answer": answer}

@app.get("/history")
async def getQueryHistory():
    historyFile = "logs/query_log.json"
    if not os.path.exists(historyFile):
        return JSONResponse(content={"history": []})
    with open(historyFile, "r") as f:
        lines = f.readlines()
        history = [json.loads(line.strip()) for line in lines]
    return JSONResponse(content={"history": history})

@app.post("/teams")
async def handle_teams(request: Request):
    data = await request.json()
    print("🔵 Incoming Teams message:", data)

    user_message = data.get("text", "").strip()
    if not user_message:
        return {"type": "message", "text": "Sorry, I didn't receive a message."}

    response_text = runQuery(user_message, [])
    return {"type": "message", "text": response_text}
