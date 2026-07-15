"""
Digital Twin — tool implementations + OpenAI function schemas.

Tools:
  1. send_email            — Resend API, emails Akshay directly
  2. save_lead             — writes lead row to Supabase `leads` table
  3. record_unknown_question — ntfy push for unanswerable questions
  4. get_availability      — reads open-to-work flag from Supabase (or env)
  5. get_latest_projects   — live GitHub public repos
  6. get_calendly_link     — returns scheduling link contextually
"""

import json
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Config ────────────────────────────────────────────────────────────────────
ntfy_topic   = os.getenv("NTFY_TOPIC", "Akshay_Notification_Portfolio_Agent")
ntfy_url     = f"https://ntfy.sh/{ntfy_topic}"

resend_key   = os.getenv("RESEND_API_KEY")
from_email   = os.getenv("FROM_EMAIL",  "twin@portfolio.dev")
to_email     = os.getenv("TO_EMAIL",    "akshaymall@utexas.edu")

supabase_url = os.getenv("SUPABASE_URL")
# Accept either key name — SUPABASE_SECRET_KEY (Supabase dashboard default) or SUPABASE_KEY
supabase_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY")

github_user  = os.getenv("GITHUB_USER", "riminator")
calendly_url = os.getenv("CALENDLY_URL", "")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _ntfy(title: str, body: str):
    """Fire-and-forget ntfy push notification."""
    try:
        requests.post(
            ntfy_url,
            data=body.encode("utf-8"),
            headers={"Priority": "3", "Title": title},
            timeout=5,
        )
    except Exception as e:
        print(f"[ntfy] failed: {e}")


def _supabase_insert(table: str, row: dict):
    """Insert a row into a Supabase table via REST. Returns True on success."""
    if not supabase_url or not supabase_key:
        return False
    try:
        resp = requests.post(
            f"{supabase_url}/rest/v1/{table}",
            json=row,
            headers={
                "apikey":        supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type":  "application/json",
                "Prefer":        "return=minimal",
            },
            timeout=8,
        )
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[supabase] insert failed: {e}")
        return False


def _supabase_select(table: str, filters: dict | None = None) -> list[dict]:
    """Select rows from a Supabase table. Returns list of dicts."""
    if not supabase_url or not supabase_key:
        return []
    try:
        params = filters or {}
        resp = requests.get(
            f"{supabase_url}/rest/v1/{table}",
            params=params,
            headers={
                "apikey":        supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Accept":        "application/json",
            },
            timeout=8,
        )
        return resp.json() if resp.status_code == 200 else []
    except Exception as e:
        print(f"[supabase] select failed: {e}")
        return []


# ── Tool 1 — send_email ───────────────────────────────────────────────────────

def send_email(name: str, email: str, message: str = "") -> str:
    """
    Send Akshay a real email via Resend when a visitor wants to connect.
    Also fires an ntfy push as a backup notification.
    """
    subject = f"Portfolio contact: {name} <{email}>"
    html = f"""
    <h2>New contact from your portfolio twin</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
    {"<p><strong>Message:</strong> " + message + "</p>" if message else ""}
    <hr>
    <p style="color:#888;font-size:12px;">Sent by your Digital Twin agent</p>
    """

    if resend_key:
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                json={"from": from_email, "to": [to_email],
                      "subject": subject, "html": html},
                headers={"Authorization": f"Bearer {resend_key}",
                         "Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (200, 201):
                _ntfy("Portfolio contact", f"{name} ({email}) wants to connect")
                return "Email sent successfully."
            else:
                print(f"[resend] error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"[resend] exception: {e}")

    # Fallback: ntfy only
    _ntfy("Portfolio contact", f"{name} ({email}) wants to connect. {message}")
    return "Notification sent."


# ── Tool 2 — save_lead ────────────────────────────────────────────────────────

def save_lead(name: str, email: str, notes: str = "") -> str:
    """
    Persist a lead to the Supabase `leads` table.

    Required table (run once in Supabase SQL editor):
        CREATE TABLE leads (
            id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            name       TEXT,
            email      TEXT NOT NULL,
            notes      TEXT,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """
    row = {
        "name":       name,
        "email":      email,
        "notes":      notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    ok = _supabase_insert("leads", row)
    return "Lead saved." if ok else "Lead could not be saved (Supabase not configured)."


# ── Tool 3 — record_unknown_question ─────────────────────────────────────────

def record_unknown_question(question: str) -> str:
    """Push an ntfy alert when a visitor asks something the agent can't answer."""
    _ntfy("Unanswered question", question)
    return "Question recorded."


# ── Tool 4 — get_availability ─────────────────────────────────────────────────

def get_availability() -> str:
    """
    Returns current open-to-work status. Reads from Supabase `settings` table
    (key='availability', value='open'|'closed'|custom message), falls back to
    the AVAILABILITY env var, then defaults to a hardcoded message.

    Supabase table (run once):
        CREATE TABLE settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        INSERT INTO settings (key, value)
        VALUES ('availability', 'open to internships and research roles for Summer 2026');
    """
    # 1. Try Supabase
    rows = _supabase_select("settings", {"key": "eq.availability", "select": "value"})
    if rows:
        return rows[0].get("value", "")

    # 2. Try env var
    env_val = os.getenv("AVAILABILITY")
    if env_val:
        return env_val

    # 3. Hardcoded default
    return "open to internships and research roles for Summer 2026"


# ── Tool 5 — get_latest_projects ─────────────────────────────────────────────

def get_latest_projects() -> str:
    """Fetch the 5 most recently updated public GitHub repos."""
    try:
        resp = requests.get(
            f"https://api.github.com/users/{github_user}/repos",
            params={"sort": "updated", "per_page": 5, "type": "public"},
            headers={"Accept": "application/vnd.github+json"},
            timeout=8,
        )
        if resp.status_code != 200:
            return "Could not fetch projects at this time."
        repos = resp.json()
        lines = []
        for r in repos:
            desc = r.get("description") or "No description"
            lines.append(f"- **{r['name']}**: {desc} ({r['html_url']})")
        return "\n".join(lines) if lines else "No public repos found."
    except Exception as e:
        print(f"[github] error: {e}")
        return "Could not fetch projects at this time."


# ── Tool 6 — get_calendly_link ────────────────────────────────────────────────

def get_calendly_link() -> str:
    """Return a Calendly scheduling link when a visitor wants to meet."""
    if calendly_url:
        return f"You can schedule a meeting here: {calendly_url}"
    return "A scheduling link isn't set up yet — please reach out via email at akshaymall@utexas.edu to arrange a time."


# ── OpenAI function schemas ───────────────────────────────────────────────────

_send_email_json = {
    "name": "send_email",
    "description": "Send Akshay a real email when a visitor wants to connect or has provided their contact info. Use this alongside save_lead whenever an email address is captured.",
    "parameters": {
        "type": "object",
        "properties": {
            "name":    {"type": "string", "description": "Visitor's name"},
            "email":   {"type": "string", "description": "Visitor's email address"},
            "message": {"type": "string", "description": "Any message or context from the conversation"},
        },
        "required": ["name", "email"],
        "additionalProperties": False,
    },
}

_save_lead_json = {
    "name": "save_lead",
    "description": "Save a visitor's contact details to the database. Always call this together with send_email when an email address is captured.",
    "parameters": {
        "type": "object",
        "properties": {
            "name":  {"type": "string", "description": "Visitor's name"},
            "email": {"type": "string", "description": "Visitor's email address"},
            "notes": {"type": "string", "description": "Context from the conversation worth saving"},
        },
        "required": ["name", "email"],
        "additionalProperties": False,
    },
}

_record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered.",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

_get_availability_json = {
    "name": "get_availability",
    "description": "Check whether Akshay is currently open to internships, jobs, or research opportunities. Call this when a visitor asks about his availability or whether he is looking for work.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

_get_latest_projects_json = {
    "name": "get_latest_projects",
    "description": "Fetch Akshay's most recently updated public GitHub repositories. Call this when a visitor asks what he is currently working on or wants to see recent projects.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

_get_calendly_link_json = {
    "name": "get_calendly_link",
    "description": "Return a link to schedule a meeting with Akshay. Call this when a visitor wants to set up a call, interview, or meeting.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

# ── Exports ───────────────────────────────────────────────────────────────────

tools = [
    {"type": "function", "function": _send_email_json},
    {"type": "function", "function": _save_lead_json},
    {"type": "function", "function": _record_unknown_question_json},
    {"type": "function", "function": _get_availability_json},
    {"type": "function", "function": _get_latest_projects_json},
    {"type": "function", "function": _get_calendly_link_json},
]

tool_map = {
    "send_email":               send_email,
    "save_lead":                save_lead,
    "record_unknown_question":  record_unknown_question,
    "get_availability":         get_availability,
    "get_latest_projects":      get_latest_projects,
    "get_calendly_link":        get_calendly_link,
}


def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"[tool] {tool_name}({arguments})", flush=True)
        tool = tool_map.get(tool_name)
        result = tool(**arguments) if tool else f"Unknown tool: {tool_name}"
        results.append({
            "role":         "tool",
            "content":      json.dumps(result),
            "tool_call_id": tool_call.id,
        })
    return results
