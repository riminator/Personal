# Portfolio — Ramaakshay Mallireddy

Personal portfolio site + AI Digital Twin agent.

**Live:**
- Portfolio → Netlify (static)
- Digital Twin API → Render (`https://portfolio-ylw8.onrender.com`)

---

## Structure

```
Portfolio/
├── static/                  # Portfolio website (Netlify)
│   ├── index.html           # Main page — all sections + floating chat bubble
│   ├── style.css            # Light/dark theme, all component styles
│   ├── assets/              # Images, PDFs, 3D models, favicons
│   ├── Dockerfile           # nginx:alpine (optional self-hosting)
│   └── nginx.conf
├── agent/                   # Digital Twin API (Render)
│   ├── app.py               # FastAPI — POST /chat, GET /health, GET /debug-env
│   ├── context.py           # System prompt loader (local files or Supabase)
│   ├── tools.py             # 6 OpenAI function-calling tools
│   ├── linkedin.pdf         # LinkedIn export (context source)
│   ├── summary.txt          # Personal summary (context source)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example         # All supported env vars with comments
│   ├── fly.toml             # Fly.io config (alternative to Render)
│   └── railway.json         # Railway config (alternative to Render)
├── docker-compose.yml       # Run full stack locally
├── netlify.toml             # Netlify build config
└── README.md
```

---

## Agent tools

| Tool | Triggers when visitor… | Requires |
|------|----------------------|----------|
| `send_email` | provides their email | `RESEND_API_KEY`, `FROM_EMAIL`, `TO_EMAIL` |
| `save_lead` | provides their email (fires with send_email) | `SUPABASE_URL`, `SUPABASE_SECRET_KEY` |
| `get_availability` | asks if Akshay is open to work | nothing — has env/DB/hardcoded fallback |
| `get_latest_projects` | asks what he's working on | nothing — uses public GitHub API |
| `get_calendly_link` | wants to schedule a meeting | `CALENDLY_URL` |
| `record_unknown_question` | asks something the agent can't answer | `NTFY_TOPIC` |

---

## Environment variables (Render)

See [`agent/.env.example`](agent/.env.example) for the full annotated list.

| Variable | Required | Notes |
|----------|----------|-------|
| `OPENAI_API_KEY` | ✅ | z.ai key |
| `OPENAI_MODEL` | ✅ | e.g. `glm-4.7-flash` |
| `OPENAI_BASE_URL` | ✅ | e.g. `https://api.z.ai/api/paas/v4/` |
| `RESEND_API_KEY` | ✅ | From resend.com |
| `FROM_EMAIL` | ✅ | `onboarding@resend.dev` until domain verified |
| `TO_EMAIL` | ✅ | Where contact emails are delivered |
| `SUPABASE_URL` | ✅ | Supabase project URL |
| `SUPABASE_SECRET_KEY` | ✅ | Supabase service role key |
| `NTFY_TOPIC` | optional | ntfy.sh push topic |
| `CALENDLY_URL` | optional | Scheduling link |
| `AVAILABILITY` | optional | Fallback if Supabase settings table not set |

---

## Supabase tables

Run once in the Supabase SQL editor:

```sql
-- Stores visitor leads (name, email, notes)
CREATE TABLE leads (
    id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name       TEXT,
    email      TEXT NOT NULL,
    notes      TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Stores dynamic settings (availability status, etc.)
CREATE TABLE settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO settings (key, value)
VALUES ('availability', 'open to internships and research roles for Summer/Fall 2026');

-- Optional: replace linkedin.pdf + summary.txt with DB-managed context
CREATE TABLE profile_context (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
INSERT INTO profile_context (key, value) VALUES
    ('summary',  'Your summary text here...'),
    ('linkedin', 'Your LinkedIn profile text here...');
```

To update your availability without redeploying:
```sql
UPDATE settings SET value = 'not currently available' WHERE key = 'availability';
```

---

## Running locally

```bash
cp agent/.env.example agent/.env   # fill in secrets
docker compose up --build

# Portfolio  → http://localhost:8080
# Agent API  → http://localhost:10000
```

Or run the agent directly without Docker:
```bash
cd agent
pip install -r requirements.txt
cp .env.example .env   # fill in secrets
python app.py
```

---

## Deploying

### Static site → Netlify (current)

**Drag & drop:** upload `Portfolio/static/` at app.netlify.com → Deploy manually.

**GitHub auto-deploy:**
1. Connect `riminator/Personal` in Netlify dashboard
2. Branch: `main` | Base directory: `Portfolio` | Publish directory: `static`
3. Leave build command blank

### Agent → Render (current)

1. New Web Service → connect `riminator/Personal`
2. Branch: `main` | Root directory: `Portfolio/agent` | Runtime: Docker
3. Add all env vars from the table above
4. Auto-deploys on every push to `main`

**Debug endpoints** (remove when no longer needed):
- `GET /debug-env` — shows which env vars are set (values masked)
- `GET /test-email` — fires a real Resend test email and returns the API response

### Alternative: Fly.io

```bash
cd agent
fly launch      # reads fly.toml
fly secrets set OPENAI_API_KEY=... RESEND_API_KEY=... # etc.
fly deploy
```

### Alternative: Railway

Connect repo → set root directory to `Portfolio/agent/` → add env vars → deploy.
`railway.json` is already configured.

---

## Updating the agent URL in the portfolio

The agent URL is set in one place in `static/index.html`:

```js
const AGENT_URL = "https://portfolio-ylw8.onrender.com";
```

Update this line if the Render service URL ever changes, then re-upload to Netlify.

---

## Upgrading Resend (custom domain)

Currently using `onboarding@resend.dev` as the sender. To use your own domain:

1. Go to [resend.com/domains](https://resend.com/domains) → Add Domain
2. Add the DNS records Resend provides to your domain registrar
3. Update `FROM_EMAIL` in Render to `twin@yourdomain.com`
4. Update `TO_EMAIL` back to `akshaymall@utexas.edu` if desired
