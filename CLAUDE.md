# CLAUDE.md — Card Game

## Project Overview

Card Game is a real-time multiplayer card game platform. The backend is a Django 5 + Django Channels application (Python 3.12) exposing REST and WebSocket APIs. The frontend is a Next.js 14 + TypeScript application with Tailwind CSS. The full stack runs via Docker Compose with Neo4j (graph DB) and Redis (WebSocket broker).

- **Language / Runtime**: Python 3.12 (backend), Node.js 20 (frontend)
- **Framework**: Django 5 + DRF + Channels (backend), Next.js 14 + TypeScript (frontend)
- **Architecture**: Service-oriented — backend REST + WebSocket API consumed by frontend SPA
- **Package / Namespace**: `card_game` (Django), `card-game-frontend` (npm)

---

## Required Skills — ALWAYS Invoke These

These skills **must** be invoked when the relevant situation arises. Never skip them.

| Situation | Skill |
|-----------|-------|
| Before any new feature or screen | `superpowers:brainstorming` |
| Planning multi-step changes | `superpowers:writing-plans` |
| Writing or fixing core logic | `superpowers:test-driven-development` |
| First sign of a bug or failure | `superpowers:systematic-debugging` |
| Before completing a feature branch | `superpowers:requesting-code-review` |
| Before claiming any task done | `superpowers:verification-before-completion` |
| Working on UI / frontend | `frontend-design:frontend-design` |
| After implementing — reviewing quality | `simplify` |

---

## Architecture

```
card-game/
├── backend/               ← Django app (Python 3.12)
│   ├── authentication/    ← JWT auth — models, views, serializers
│   ├── game/              ← Core game logic, WebSocket consumers, models
│   ├── api/               ← Root REST endpoints
│   └── card_game/         ← Django settings, ASGI, URLs
├── frontend/              ← Next.js 14 (Node 20)
│   └── src/
│       ├── components/    ← React UI components
│       ├── pages/         ← Next.js pages (SSR/CSR)
│       ├── services/      ← API + WebSocket clients
│       └── utils/         ← Pure utility functions
├── docker/                ← Dockerfiles
├── website/               ← GitHub Pages static site
└── docker-compose.yml     ← Full stack
```

### Layer Rules

- `frontend/src/services/` must not contain UI logic — API calls only
- `backend/game/` must not import from `backend/authentication/` models directly — use `settings.AUTH_USER_MODEL`
- WebSocket consumers live in `backend/game/consumers.py`

---

## Coding Conventions

- [ ] All models are **immutable** — use `copy()` / spread for mutations
- [ ] Functions are **pure** where possible — no hidden side effects
- [ ] State is a single source of truth per feature
- [ ] No hardcoded strings — use constants, config, or i18n resources
- [ ] Strict typing everywhere (TypeScript strict, typed Python with mypy-compatible annotations)

---

## Engineering Principles

### File Size

- **200-line maximum per file** — extract a class, function, or module when approaching the limit

### DRY · SOLID · KISS · YAGNI

- Extract shared logic into named utilities; never copy-paste
- Single Responsibility: one class/function does one thing
- Don't add features not yet needed
- Delete dead code immediately

### TDD

- Write the failing test first, make it pass, then refactor
- Test names describe behaviour: `"should reject duplicate email"`
- One assertion per test — keep tests focused and readable

### Commit hygiene

- Follow Conventional Commits: `feat: ...` / `fix: ...` / `chore: ...`
- The `commit-msg` hook enforces this automatically

---

## Build Commands

```bash
# Full stack
docker-compose up

# Backend
cd backend
pip install -r requirements.txt
python manage.py runserver          # Dev server
pytest tests/ -x                    # Tests
ruff check .                        # Lint
pytest tests/ -x && ruff check .    # Smoke

# Frontend
cd frontend
npm install
npm run dev                         # Dev server
npm run build                       # Build
npm test -- --watchAll=false        # Tests
npm run lint                        # Lint
npm run lint && npm test -- --watchAll=false  # Smoke
```

---

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file — project conventions and session startup |
| `version.txt` | Semantic version (MAJOR.MINOR.PATCH) |
| `docker-compose.yml` | Full stack orchestration |
| `backend/card_game/settings.py` | Django settings |
| `backend/game/consumers.py` | WebSocket consumers |
| `.github/workflows/` | CI, release, Pages automation |
| `.githooks/` | Pre-commit and commit-msg hooks |
| `scripts/install-hooks.sh` | One-time hook installer |

---

## Starting a New Session

1. Read this file
2. Run `cd backend && pytest tests/ -x && ruff check .` to confirm backend passes
3. Run `cd frontend && npm run lint && npm test -- --watchAll=false` to confirm frontend passes
4. Invoke `superpowers:brainstorming` before touching any feature
5. Follow the Required Skills table — every skill is mandatory, not optional
