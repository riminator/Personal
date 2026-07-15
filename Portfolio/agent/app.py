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

MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
API_URL = os.getenv("OPENAI_BASE_URL")   # set this in Render if using a non-OpenAI provider

app = FastAPI(title="Digital Twin API")

# Allow the portfolio (any origin) to call this API.
# Tighten origins to your Netlify URL in production if desired.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

client = OpenAI(base_url=API_URL) if API_URL else OpenAI()
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


@app.get("/debug-env")
def debug_env():
    """Shows which env vars are set (values masked) — remove after debugging."""
    def present(key):
        val = os.getenv(key)
        if not val:
            return "❌ NOT SET"
        return f"✅ set ({val[:6]}...)" if len(val) > 6 else "✅ set"

    return {
        "RESEND_API_KEY":      present("RESEND_API_KEY"),
        "FROM_EMAIL":          os.getenv("FROM_EMAIL", "❌ NOT SET"),
        "TO_EMAIL":            os.getenv("TO_EMAIL",   "❌ NOT SET"),
        "SUPABASE_URL":        present("SUPABASE_URL"),
        "SUPABASE_SECRET_KEY": present("SUPABASE_SECRET_KEY"),
        "OPENAI_MODEL":        os.getenv("OPENAI_MODEL", "❌ NOT SET"),
        "OPENAI_BASE_URL":     os.getenv("OPENAI_BASE_URL", "❌ NOT SET"),
        "NTFY_TOPIC":          os.getenv("NTFY_TOPIC", "default"),
        "CALENDLY_URL":        os.getenv("CALENDLY_URL", "❌ NOT SET"),
        "AVAILABILITY":        os.getenv("AVAILABILITY", "default"),
    }


@app.get("/test-email")
def test_email():
    """Trigger a test Resend email and return the full response — remove after debugging."""
    import os, requests as req
    key       = os.getenv("RESEND_API_KEY")
    from_addr = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
    to_addr   = os.getenv("TO_EMAIL",   "akshaymall@utexas.edu")
    if not key:
        return {"error": "RESEND_API_KEY not set"}
    try:
        resp = req.post(
            "https://api.resend.com/emails",
            json={"from": from_addr, "to": [to_addr],
                  "subject": "Digital Twin — test email",
                  "html": "<h2>Test</h2><p>If you see this, Resend is working!</p>"},
            headers={"Authorization": f"Bearer {key}",
                     "Content-Type": "application/json"},
            timeout=10,
        )
        return {"status_code": resp.status_code, "body": resp.json()}
    except Exception as e:
        return {"error": str(e)}


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
