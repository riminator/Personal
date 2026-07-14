# Portfolio Context — Ramaakshay Mallireddy

> Quick-reference doc for Bob to understand this repository at a glance. Read this before making any changes to the portfolio.

---

## What This Is

A **single-page personal portfolio website** for **Ramaakshay (Akshay) Mallireddy**, an Aerospace Engineering student at the University of Texas at Austin. The site is static HTML/CSS with no build tooling, no JavaScript framework, and no backend.

- **Live file:** `Portfolio/index.html`
- **Styles:** `Portfolio/style.css`
- **Assets:** all in `Portfolio/` (images, PDFs, 3D model files, favicons)

---

## Owner / Identity

| Field | Value |
|---|---|
| Full name | Ramaakshay Mallireddy |
| Preferred name | Akshay |
| University | The University of Texas at Austin |
| Major | Aerospace Engineering |
| Expected Graduation | May 2028 |
| Email | akshaymall@utexas.edu |
| LinkedIn | https://www.linkedin.com/in/ramaakshay-mallireddy |
| GitHub | https://github.com/riminator |

---

## Site Structure (Sections)

| Section ID | Nav Label | Purpose |
|---|---|---|
| `#home` | Home | Hero — photo, name, tagline, CTA buttons, social links |
| `#Coding` | Code | Five coding/research project cards (purple accent) |
| `#CAD` | CAD | Four CAD/engineering project cards (blue accent) + AIAA PDF report |
| `#Classes` | Classes | Completed & current coursework in two-column card grid |
| `#Resume` | Resume | Embedded PDF + download button |
| `#Contact` | Contact | Centered contact card with email button + social icons |

Navigation is a fixed 64px frosted-glass header. Active nav link is set via `IntersectionObserver` (not scroll events).
Section dividers (`<div class="section-divider">`) separate each section visually.

---

## Design System (style.css)

### Design Direction
Dark-mode, minimal, refined. No light theme. Inspired by modern developer portfolio aesthetics.

### Fonts
- **Body/UI:** `Inter` (Google Fonts) — weights 300–800
- **Code/pills:** `JetBrains Mono` (Google Fonts) — weights 400, 500

### CSS Custom Properties (`:root`)
```css
--bg:          #0a0a0f      /* page background */
--surface:     #111118      /* card/section background */
--surface-2:   #1a1a24      /* hover backgrounds */
--surface-3:   #22222f      /* deeper surface */
--border:      rgba(255,255,255,0.08)
--border-hover:rgba(255,255,255,0.18)
--text:        #e8e8f0
--text-muted:  #8888a0
--text-dim:    #5a5a72
--blue:        #4f8ef7      /* CAD section accent */
--purple:      #a78bfa      /* Coding section accent */
--orange:      #f97316      /* UT Austin, Resume accent */
--green:       #34d399      /* Classes "current" dot */
--red:         #f87171      /* PDF icon */
```

### Key CSS Classes
| Class | Purpose |
|---|---|
| `.section-heading` | Flex row: icon-wrap + h1 + decorative line |
| `.project-card.detailed` | 2-col grid card (1.4fr / 1fr). Collapses to 1 col on mobile |
| `.project-info` | Left column of a project card |
| `.project-media` | Right column — contains the image |
| `.project-section` | Sub-block inside `.project-info` (Overview, Tech Details, Skills) |
| `.skills` | Flex wrap of pill `<li>` items (monospace font) |
| `.section-divider` | 1px horizontal rule between sections |
| `.classes-grid` | 2-col grid for coursework cards |
| `.classes-card` | Individual coursework card (`.completed` or `.current`) |
| `.resume-wrapper` | Resume embed container |
| `.contact-inner` | Centered contact card |
| `.btn-primary` | Blue filled CTA button |
| `.btn-ghost` | Ghost/outline button |
| `.social-row` | Row of square icon links |

### Per-section CSS Scoping
```css
.CAD .project-card.detailed    { --card-accent: var(--blue); }
.Coding .project-card.detailed { --card-accent: var(--purple); }
```
The `--card-accent` variable controls the top border gradient, icon color, and skill pill style on hover.

---

## Coding Projects (5 total)

### 1. IL & RL Blended Recovery Architecture
- **Context:** Robot Learning FRI research, UT Austin
- **Stack:** Python, PyTorch, Actor-Critic RL, Behavior Cloning
- Dual-policy framework: IL for nominal states + deep RL recovery for OOD states
- Safety-constrained action projection (shielding layer) prevents collisions

### 2. AI-Powered Hybrid Cloud Solutions — IBM
- **Context:** IBM Software/Platform Engineering Intern (May–Aug 2026)
- **Stack:** Python, Java, Docker, Kubernetes, Red Hat OpenShift, IBM Cloud
- Cloud-native workloads for enterprise clients; proof-of-concept architectures

### 3. Orbital Energy Simulation — Texas Spacecraft Lab
- **Context:** TSL Electrical Power Systems sub-team (Sep 2025–current)
- **Stack:** MATLAB, PCB Design, Power Systems
- EGSE PCB design + orbital energy simulations; ±5% prediction accuracy

### 4. Electrical Grid Simulation Automation — Austin Energy
- **Context:** Electrical Engineering Intern (Jun–Aug 2024)
- **Stack:** Python, Automation, AutoCAD AUD
- Automated 200+ grid simulations; designed 10+ electrical implementations

### 5. Celestial Body Detection Research
- **Context:** National High School Journal of Science (May–Aug 2025)
- Tested 10+ detection methods; peer-reviewed publication, cited by others

---

## CAD Projects (4 total)

### 1. Headphone Stand
- **File refs:** `project_1.jpg`, `headphone_stand.obj/.mtl`
- Fusion 360 parametric design; FDM-optimized with AirPods Pro holder

### 2. F-18 Remastered
- **File refs:** `project_2.jpg`, `F-18 Remastered.obj/.mtl`
- High-fidelity parametric surface model; wing–body blending, CFD-ready topology

### 3. CubeSat with Liquid Propulsion
- **File refs:** `project_3.jpg`, `CubeSat.obj/.mtl`
- Subsystem-level CubeSat with liquid propulsion, CoM-stable thruster placement

### 4. Autonomous Navy Fighter Jet — AIAA
- **File refs:** `project_4.jpg`
- AIAA Aircraft Design Competition; Mach 1.8, stealth, autonomous, carrier-compatible
- **Report:** `2026_The University of Texas at Austin_DESIGN_REPORT.pdf`

---

## Coursework

### Completed
- Multivariable Calculus (M408D)
- AI Design and Development (ITD111)
- Computer Programming (Python) (CS303E)
- C++ Data Structures & Algorithms (COE301)
- Differential Equations & Linear Algebra (M427J)
- Statics (E M 303)
- Thermodynamics (ME 310T)
- Robot Learning (CS 309)
- Engineering Computation (COE 311K)

### Current
- Vector Calculus (M427L)
- Dynamics (E M 311M)
- Mechanics of Solids (E M 319)
- Robot Learning FRI II (C S 378)
- Engineering Communication (E S 333T)

---

## JavaScript Behaviour

### IntersectionObserver Active Nav
```js
// Observes each <section>, updates nav active state when section enters viewport
// rootMargin: "-40% 0px -55% 0px" — triggers when section is in middle band
const observer = new IntersectionObserver(...)
sections.forEach(section => observer.observe(section));
```
Replaces the old scroll event listener. More performant and accurate.

---

## Asset Inventory

| File | Type | Used For |
|---|---|---|
| `main.jpeg` | Image | Hero headshot |
| `project_1.jpg` | Image | Headphone Stand card |
| `project_2.jpg` | Image | F-18 Remastered card |
| `project_3.jpg` | Image | CubeSat card + Coding section placeholder images |
| `project_4.jpg` | Image | Fighter Jet card + Coding section placeholder images |
| `Ramaakshay_Mallireddy_Resume.pdf` | PDF | Resume section embed + download |
| `2026_The University of Texas at Austin_DESIGN_REPORT.pdf` | PDF | AIAA report embed + download |
| `headphone_stand.obj/.mtl` | 3D model | Headphone Stand (download only) |
| `F-18 Remastered.obj/.mtl` | 3D model | F-18 (download only) |
| `CubeSat.obj/.mtl` | 3D model | CubeSat (download only) |
| `favicon.*`, `android-chrome-*`, `apple-touch-icon.png` | Icons | Browser/PWA |
| `site.webmanifest` | PWA | Web app manifest |
| `project_2_preview.png`, `project3_preview.png`, `project4_preview.png`, `headphones_stand_preview.jpg` | Legacy | Not currently used in HTML |

---

## Common Tasks Bob Should Know

| Task | Where to edit |
|---|---|
| Add a new coding project | Add `.project-card.detailed` block inside `<section class="Coding">` in `index.html` |
| Add a new CAD project | Add `.project-card.detailed` block inside `<section class="CAD">` in `index.html` |
| Change coding section accent color | Edit `--purple` in `:root` in `style.css` |
| Change CAD section accent color | Edit `--blue` in `:root` in `style.css` |
| Update coursework | Edit `<ul>` items inside `.classes-card.completed` or `.classes-card.current` |
| Replace resume PDF | Swap `Ramaakshay_Mallireddy_Resume.pdf` in `Portfolio/` |
| Update social links | Three places: `.home .social-row`, `.contact-inner .social-row`, and the `href` values |
| Add a new section | Add `<section>` in `index.html` + nav `<a>` in `<header>` + styles in `style.css` |
| Update hero tagline/bio | Edit `<p>` inside `.home-content` in `index.html` |
| Add project images | Drop images in `Portfolio/` and update `src` attributes on `.project-media img` |

---

## Known Quirks / Notes

- Coding section cards currently reuse `project_3.jpg` and `project_4.jpg` as placeholder images. Each should get its own dedicated screenshot/image when available.
- Favicon paths were changed from root-relative (`/favicon-32x32.png`) to relative (`favicon-32x32.png`) — correct for serving from a subdirectory.
- 3D `.obj/.mtl` files are present in `Portfolio/` but are not rendered in-browser. They exist for download/reference.
- No build step — all changes are immediately reflected on browser refresh.
