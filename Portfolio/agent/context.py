"""
Context loader for the Digital Twin agent.

Data sources (priority order):
  1. Supabase database  — when SUPABASE_URL + SUPABASE_KEY are set (future)
  2. Local files        — linkedin.pdf + summary.txt (current default)

To enable Supabase later, set the env vars and update `_load_from_supabase`.
"""
import os
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv(override=True)

# ──────────────────────────────────────────────────────────────────────────────
# 1. Supabase loader (stub — wire this up when the DB is ready)
# ──────────────────────────────────────────────────────────────────────────────

def _load_from_supabase() -> tuple[str, str] | None:
    """
    Returns (summary, linkedin_text) from Supabase, or None if not configured.

    Expected table: `profile_context`
    Expected columns:
        - key   TEXT PRIMARY KEY  (e.g. 'summary', 'linkedin')
        - value TEXT
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        return None
    try:
        from supabase import create_client  # pip install supabase
        client = create_client(url, key)
        rows = client.table("profile_context").select("key,value").execute().data
        data = {r["key"]: r["value"] for r in rows}
        return data.get("summary", ""), data.get("linkedin", "")
    except Exception as e:
        print(f"[context] Supabase load failed, falling back to local files: {e}")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# 2. Local file loader (always works; used when Supabase is not configured)
# ──────────────────────────────────────────────────────────────────────────────

def _load_from_files() -> tuple[str, str]:
    base = os.path.dirname(__file__)

    reader = PdfReader(os.path.join(base, "linkedin.pdf"))
    linkedin = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedin += text

    with open(os.path.join(base, "summary.txt"), "r", encoding="utf-8") as f:
        summary = f.read()

    return summary, linkedin


# ──────────────────────────────────────────────────────────────────────────────
# 3. Pick the right source
# ──────────────────────────────────────────────────────────────────────────────

_result = _load_from_supabase() or _load_from_files()
summary, linkedin = _result

TWIN_SYSTEM_PROMPT = f"""
# Your role

You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:

{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context

Here is a summary of the person's LinkedIn profile so that you can answer questions:

{linkedin}

# Rules

Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Only answer questions related to career, background, skills and experience.
If the user asks about something unrelated, then steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

If the user would like to get in touch, ask for their name and email, then call BOTH `send_email` AND `save_lead` together.

If a visitor asks about availability or whether Akshay is looking for work, call `get_availability` to get the live answer.

If a visitor asks what Akshay is currently working on or wants to see recent projects, call `get_latest_projects`.

If a visitor wants to schedule a call, interview, or meeting, call `get_calendly_link`.

IMPORTANT:
If you don't know the answer, use your tool to record the question, and then tell the user that you don't know. Never make up an answer.

Use styling (in markdown, no code blocks) to make the response more engaging and easy to read.
""".strip()
