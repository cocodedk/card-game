# Card Game

A modern real-time multiplayer card game platform built with Django, Next.js, WebSockets, and Neo4j. Play customizable card games with friends — authentication, live gameplay, and game history all included.

## Website

- [English](https://cocodedk.github.io/card-game/)
- [فارسی (Persian)](https://cocodedk.github.io/card-game/fa/)

## Features

- Real-time multiplayer gameplay via WebSockets (Django Channels + Redis)
- JWT-based authentication with refresh tokens
- Customizable decks and cards backed by Neo4j graph database
- Full game state tracking, history, and statistics
- One-command Docker Compose setup for the full stack
- Responsive Next.js + Tailwind CSS frontend

## Build from Source

**Prerequisites:** Docker + Docker Compose, Node.js 20+, Python 3.12+

```bash
# Clone
git clone https://github.com/cocodedk/card-game.git
cd card-game

# Full stack via Docker
docker-compose up

# Backend only
cd backend && pip install -r requirements.txt
python manage.py runserver

# Frontend only
cd frontend && npm install && npm run dev
```

**Test:**
```bash
# Backend tests
cd backend && pytest tests/ -x

# Frontend tests
cd frontend && npm test

# Frontend lint
cd frontend && npm run lint
```

## Architecture

```
card-game/
├── backend/               ← Django 5 + DRF + Channels (Python 3.12)
│   ├── authentication/    ← JWT auth app
│   ├── game/              ← Game logic, WebSocket consumers, API
│   ├── api/               ← Root API endpoints
│   └── card_game/         ← Django settings, ASGI config
├── frontend/              ← Next.js 14 + TypeScript + Tailwind (Node 20)
│   └── src/               ← Components, pages, services, utils
├── docker/                ← Dockerfiles for backend and frontend
├── website/               ← GitHub Pages bilingual site
└── docker-compose.yml     ← Full stack orchestration
```

| Layer | Tech |
|---|---|
| Backend | Django 5, DRF 3.14, Django Channels 4, Daphne |
| Frontend | Next.js 14, TypeScript 5.3, Tailwind CSS 3.4, TanStack Query |
| Database | Neo4j 5.16 (Neomodel), SQLite (dev) |
| Infra | Docker Compose, Redis 7.2, WebSockets |

## Docker

```bash
docker-compose up
```

Services: `http://localhost:3000` (frontend) · `http://localhost:8000/api/` (API) · `http://localhost:7474` (Neo4j)

## Author

**Babak Bandpey** — [cocode.dk](https://cocode.dk) | [LinkedIn](https://linkedin.com/in/babakbandpey) | [GitHub](https://github.com/cocodedk)

---

Apache-2.0 | © 2026 [Cocode](https://cocode.dk) | Created by [Babak Bandpey](https://linkedin.com/in/babakbandpey)
