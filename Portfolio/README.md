# Portfolio — Akshay Mallireddy

Personal portfolio and AI Digital Twin agent.

```
Portfolio/
├── static/          # Static HTML/CSS portfolio site
│   ├── index.html
│   ├── style.css
│   ├── assets/      # Images, PDFs, 3D models, favicons
│   ├── Dockerfile   # nginx:alpine image for static hosting
│   └── nginx.conf
├── agent/           # Gradio + OpenAI Digital Twin chatbot
│   ├── app.py
│   ├── context.py   # Loads profile data (files or Supabase)
│   ├── tools.py     # OpenAI function-calling tools
│   ├── styles.py    # Gradio CSS/JS
│   ├── linkedin.pdf
│   ├── summary.txt
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── fly.toml     # Fly.io config
│   └── railway.json # Railway config
└── docker-compose.yml
```

---

## Running locally

```bash
cp agent/.env.example agent/.env   # add OPENAI_API_KEY etc.
docker compose up --build

# Static site → http://localhost:8080
# Digital Twin → http://localhost:7860
```

---

## Deployment options

### Option 1 — Fly.io (Recommended)

Best for: always-on agent + free tier, close to UT Austin (Dallas region).

```bash
# Install CLI: https://fly.io/docs/hands-on/install-flyctl/
brew install flyctl
fly auth login

# Deploy the agent
cd agent
fly launch          # first time — reads fly.toml, creates the app
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set NTFY_TOPIC=Akshay_Notification_Portfolio_Agent
fly deploy          # subsequent deploys

# Deploy the static site (optional — see Option 2 for Cloudflare Pages)
cd ../static
fly launch --name akshay-portfolio
fly deploy
```

Agent URL will be: `https://akshay-digital-twin.fly.dev`  
Update the two `https://your-agent-url.fly.dev` placeholders in `static/index.html`.

---

### Option 2 — Railway

Best for: simpler UI, auto-deploy from GitHub push.

1. Push this repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**.
3. Select the repo, set **Root Directory** to `agent/`.
4. Add environment variables: `OPENAI_API_KEY`, `NTFY_TOPIC`.
5. Railway reads `railway.json` automatically — no config needed.
6. Agent URL shows in the Railway dashboard.

For the static site, deploy `static/` as a second Railway service (static serving) or use Cloudflare Pages.

---

### Option 3 — Cloudflare Pages (Static Site) + Fly.io (Agent)

The cleanest production split:

| Part | Platform | Why |
|------|----------|-----|
| `static/` | Cloudflare Pages | CDN edge, free, auto-deploy from GitHub |
| `agent/` | Fly.io | Docker, always-on, scales to 0 when idle |

**Cloudflare Pages:**
1. Connect GitHub repo in Cloudflare dashboard.
2. Set Build output directory: `Portfolio/static`.
3. No build command needed — it's plain HTML.

**After deploying the agent**, replace the two `your-agent-url.fly.dev` placeholders in `static/index.html`:
```html
<!-- Both occurrences: -->
href="https://akshay-digital-twin.fly.dev"
src="https://akshay-digital-twin.fly.dev"
```

---

### Option 4 — Render

Similar to Railway with a generous free tier.

1. New Web Service → connect GitHub.
2. Root directory: `agent/`.
3. Runtime: **Docker**.
4. Set env vars in dashboard.
5. Free tier spins down after 15 min of inactivity (cold start ~30s).

---

## Enabling Supabase context (future)

The agent is pre-wired in [`agent/context.py`](agent/context.py) to pull profile data from Supabase when credentials are present. To enable:

1. Create a Supabase project at [supabase.com](https://supabase.com).
2. Run this SQL in the Supabase SQL editor:
   ```sql
   CREATE TABLE profile_context (
     key   TEXT PRIMARY KEY,
     value TEXT NOT NULL
   );

   INSERT INTO profile_context (key, value) VALUES
     ('summary',  'Your summary text here...'),
     ('linkedin', 'Your LinkedIn profile text here...');
   ```
3. Add to `agent/.env` (or fly secrets / Railway env vars):
   ```
   SUPABASE_URL=https://xxxx.supabase.co
   SUPABASE_KEY=your-anon-or-service-role-key
   ```
4. Uncomment `supabase>=2.0` in `agent/requirements.txt`.
5. Redeploy. The agent will now pull from the DB — update content without redeploying.

---

## Updating the iframe URL

Once deployed, find both occurrences of `your-agent-url.fly.dev` in `static/index.html` and replace with your real agent URL.
