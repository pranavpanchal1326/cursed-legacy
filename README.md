# Cursed Legacy
### AI-Powered Dark Fantasy RPG • Narrative Intelligence + Deterministic Combat

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Gemini](https://img.shields.io/badge/AI-Gemini_2.0-8E44AD?style=for-the-badge)
![RPG](https://img.shields.io/badge/Genre-Dark_Fantasy_RPG-8B0000?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-2E8B57?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-1E90FF?style=for-the-badge)

**A cinematic, replayable dark fantasy RPG powered by adaptive AI storytelling and robust RPG systems.**

</div>

---

## Table of Contents

- [1. Product Overview](#1-product-overview)
- [2. Key Features](#2-key-features)
- [3. Gameplay Systems](#3-gameplay-systems)
- [4. Architecture](#4-architecture)
  - [4.1 High-Level Block Diagram](#41-high-level-block-diagram)
  - [4.2 Turn Processing Sequence](#42-turn-processing-sequence)
  - [4.3 Runtime Data Flow](#43-runtime-data-flow)
- [5. Tech Stack](#5-tech-stack)
- [6. Project Structure](#6-project-structure)
- [7. Installation](#7-installation)
- [8. Configuration](#8-configuration)
- [9. Running the Project](#9-running-the-project)
- [10. API Surface (Flask Endpoints)](#10-api-surface-flask-endpoints)
- [11. Security & Reliability](#11-security--reliability)
- [12. Testing & Quality Gates](#12-testing--quality-gates)
- [13. Deployment](#13-deployment)
- [14. Performance Guidelines](#14-performance-guidelines)
- [15. Observability](#15-observability)
- [16. Roadmap](#16-roadmap)
- [17. Contributing](#17-contributing)
- [18. License](#18-license)

---

## 1. Product Overview

**Cursed Legacy** is a 30-turn, AI-directed RPG where narrative variance is high, but gameplay logic remains deterministic and testable.

The game fuses:
- **Generative storytelling** via Google Gemini
- **Class + path-driven combat mechanics**
- **Morality-based campaign shaping**
- **Achievement and progression systems**

Each run maintains core structural integrity while producing unique outcomes.

---

## 2. Key Features

### Narrative Intelligence
- Dynamic turn-by-turn story generation (80–120 words)
- Campaign escalation and dramatic beats at turns **10** and **20**
- Context-aware story continuity using current player state

### RPG Combat Engine
- Type advantages and weaknesses
- Ability and equipment modifiers
- Scaling difficulty over campaign phases

### Progression Layer
- 4 classes, 10 story paths, 14 equipment items
- 10-tier power ladder (*Weak Human → ABSOLUTE POWER*)
- 10 unlockable achievements

### Moral Alignment System
- Alignment values from `-18` (corrupt) to `+12` (virtuous)
- Alignment affects tone, encounter consequences, and resolution arcs

---

## 3. Gameplay Systems

### Story Paths (10)
- Cursed King
- Demon Blood
- Special Grade
- Rogue Shinobi
- Vampire King
- One-Eyed Ghoul
- Chainsaw Devil
- Hollow King
- Nen Master
- Black Swordsman

### Character Classes (4)
- Berserker
- Cursed Caster
- Shadow Assassin
- Blood Priest

### Campaign Structure
- **Turns 1–9:** Build-up and faction framing
- **Turn 10:** Major narrative rupture
- **Turns 11–19:** Complications + counterforce escalation
- **Turn 20:** Second critical inversion
- **Turns 21–30:** Endgame convergence and final fate

---

## 4. Architecture

## 4.1 High-Level Block Diagram

```text
┌────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                           │
│  Browser UI (HTML/CSS/JS)                                         │
│  - Character creation                                              │
│  - Choice submission                                               │
│  - Combat view + notifications                                     │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTP/JSON
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                         FLASK APPLICATION                          │
│  app.py                                                            │
│  - Routing / request validation                                    │
│  - Session + game-state orchestration                              │
│  - Error handling / response shaping                               │
└───────────────┬───────────────────────────────┬────────────────────┘
                │                               │
                ▼                               ▼
┌─────────────────────────────┐      ┌──────────────────────────────┐
│      GAME DOMAIN LAYER      │      │      AI NARRATIVE LAYER      │
│ game/engine.py              │      │ game/ai_story.py             │
│ game/combat.py              │◄────►│ - Prompt builder             │
│ game/morality.py            │      │ - Safety constraints         │
│ game/progression.py         │      │ - Gemini API integration     │
│ game/achievements.py        │      │ - Response normalization      │
└───────────────┬─────────────┘      └───────────────┬──────────────┘
                │                                    │
                ▼                                    ▼
┌─────────────────────────────┐      ┌──────────────────────────────┐
│     STATE + CONFIG LAYER    │      │      EXTERNAL PROVIDER       │
│ Session / cache / save data │      │ Google Gemini API            │
│ Env config (.env)           │      │ (LLM generation endpoint)    │
└─────────────────────────────┘      └──────────────────────────────┘
```

---

## 4.2 Turn Processing Sequence

```text
Player Action
   │
   ▼
[Flask Route] /api/turn
   │ validate payload
   ▼
[Game Engine]
   ├─ Apply choice consequences
   ├─ Resolve combat (if encounter)
   ├─ Update morality + progression
   └─ Build compact narrative context
   │
   ▼
[AI Story Service]
   ├─ Build constrained prompt
   ├─ Call Gemini API
   └─ Normalize output length/style
   │
   ▼
[Game Engine]
   ├─ Persist turn state
   ├─ Check achievements
   └─ Detect end condition
   │
   ▼
JSON Response → UI render + animation + notifications
```

---

## 4.3 Runtime Data Flow

```text
UI State
  └── choice + action payload
        ↓
Flask Controller
  └── normalized command object
        ↓
Domain Services
  ├── CombatResult
  ├── MoralityDelta
  ├── ProgressionDelta
  └── TurnSummary
        ↓
Prompt Assembler
  └── context window (compact)
        ↓
Gemini Completion
  └── story segment
        ↓
Response Composer
  └── narrative + stats + unlocked events
        ↓
Frontend Renderer
```

---

## 5. Tech Stack

- **Backend:** Python 3.10+, Flask 3.x
- **AI:** Google Gemini 2.0
- **Frontend:** HTML, CSS, Vanilla JS
- **State:** Flask session / server-side runtime model
- **Environment:** `.env` via python-dotenv
- **Testing:** pytest (recommended)

---

## 6. Project Structure

```text
cursed-legacy/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── game/
│   ├── __init__.py
│   ├── engine.py
│   ├── combat.py
│   ├── morality.py
│   ├── progression.py
│   ├── achievements.py
│   └── ai_story.py
├── templates/
│   ├── index.html
│   └── game.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── game.js
    └── assets/
```

---

## 7. Installation

### Prerequisites
- Python `3.10+`
- `pip`
- Gemini API key

### Setup

```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
python -m venv .venv
```

#### Windows (PowerShell)
```powershell
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 8. Configuration

Create `.env` in project root:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=replace_with_secure_random_string
FLASK_ENV=development
FLASK_DEBUG=1
```

### `.env.example` (recommended)
```env
GEMINI_API_KEY=
SECRET_KEY=
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## 9. Running the Project

### Development
```bash
python app.py
```
or
```bash
flask run
```

App URL: `http://127.0.0.1:5000`

### Production (Gunicorn)
```bash
gunicorn -w 4 -k gthread -b 0.0.0.0:8000 app:app
```

---

## 10. API Surface (Flask Endpoints)

> Adjust endpoint names to match your implementation.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Landing page |
| GET | `/game` | Main game interface |
| POST | `/api/start` | Initialize new run |
| POST | `/api/turn` | Submit choice, resolve one turn |
| GET | `/api/state` | Fetch current game state |
| POST | `/api/reset` | Reset session/run |

### Example `POST /api/turn` request
```json
{
  "choice_id": "attack_frontline",
  "stance": "aggressive",
  "ability": "domain_expansion"
}
```

### Example response
```json
{
  "turn": 12,
  "narrative": "The shrine fractures the moonlight...",
  "combat": {
    "player_hp": 72,
    "enemy_hp": 38,
    "result": "advantage"
  },
  "morality": -6,
  "power_level": "High Cursed Entity",
  "achievements_unlocked": ["First Blood Moon"]
}
```

---

## 11. Security & Reliability

- Store all secrets in environment variables
- Never expose API keys to frontend
- Add request timeout for LLM calls
- Sanitize and bound user inputs
- Add fallback text generation when LLM is unavailable
- Include global exception handling for stable UX

---

## 12. Testing & Quality Gates

### Recommended test coverage
- Combat outcome determinism
- Morality delta correctness
- Turn progression invariants (1→30)
- Achievement trigger integrity
- API contract snapshots for `/api/turn`

### Run tests
```bash
pytest -q
```

### Lint/format (recommended)
```bash
ruff check .
black .
```

---

## 13. Deployment

### Option A: Render / Railway / Fly.io
- Set build command: `pip install -r requirements.txt`
- Start command: `gunicorn -w 4 -k gthread -b 0.0.0.0:$PORT app:app`
- Add env vars in platform dashboard

### Option B: VPS + Nginx + Gunicorn
- Run Gunicorn behind Nginx reverse proxy
- Enable HTTPS (Let’s Encrypt)
- Configure service restart with systemd

---

## 14. Performance Guidelines

- Keep prompt context compact and state-driven
- Cache static assets with long max-age
- Debounce repeated action submissions client-side
- Use structured turn summaries instead of full history replay
- Monitor LLM latency p95 and timeout rate

---

## 15. Observability

Recommended logging fields per turn:
- `run_id`
- `turn_index`
- `path`
- `class`
- `morality_before`
- `morality_after`
- `combat_result`
- `llm_latency_ms`
- `llm_status`

This enables rapid debugging for continuity drift and balance issues.

---

## 16. Roadmap

- Save/Load slots
- New Game+ modifiers
- Procedural boss archetypes
- Additional path-exclusive endings
- Deterministic seed mode for replay comparisons
- Telemetry dashboard for balance tuning

---

## 17. Contributing

1. Fork repository
2. Create feature branch:
   ```bash
   git checkout -b feat/<feature-name>
   ```
3. Commit changes:
   ```bash
   git commit -m "feat: add <feature-name>"
   ```
4. Push branch and open PR

### Commit style (recommended)
- `feat:`
- `fix:`
- `refactor:`
- `docs:`
- `test:`
- `chore:`

---

## 18. License

MIT License — see `LICENSE`.

---

<div align="center">

**Cursed Legacy — engineered as a showcase-grade fusion of AI narrative generation and RPG systems design.**

</div>
