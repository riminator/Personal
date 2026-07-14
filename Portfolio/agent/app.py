"""
Digital Twin — FastAPI backend
POST /chat  { "message": "...", "history": [...] }  →  { "reply": "..." }
GET  /health  →  200 OK
"""
import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

from context import TWIN_SYSTEM_PROMPT
from tools import tools, handle_tool_calls

load_dotenv(override=True)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

app = FastAPI(title="Digital Twin API")

# Allow the portfolio (any origin) to call this API.
# Tighten origins to your Netlify URL in production if desired.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

client = OpenAI()
system_msg = {"role": "system", "content": TWIN_SYSTEM_PROMPT}


class ChatRequest(BaseModel):
    message: str
    # Each item: {"role": "user"|"assistant", "content": "..."}
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    messages = [system_msg] + req.history + [{"role": "user", "content": req.message}]
    response = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools
    )
    # Handle tool calls in a loop
    while response.choices[0].finish_reason == "tool_calls":
        msg = response.choices[0].message
        tool_results = handle_tool_calls(msg.tool_calls)
        messages.append(msg)
        messages.extend(tool_results)
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
    return ChatResponse(reply=response.choices[0].message.content)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
