# Contributing to Card Game

## Local Setup

1. Install Docker and Docker Compose.
2. Ensure Python 3.12+ and Node.js 20+ are available for local development.
3. Clone the repo and run `docker-compose up` to start all services.

## Install Git Hooks

```sh
./scripts/install-hooks.sh
```

## Local Git Setup

Run these once after cloning:

```bash
git config pull.rebase true
git config core.autocrlf input
git config push.autoSetupRemote true
git config init.defaultBranch main
```

## Build and Test Commands

**Backend:**
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -x
ruff check .
```

**Frontend:**
```bash
cd frontend
npm install
npm run lint
npm test
npm run build
```

**Full stack (Docker):**
```bash
docker-compose up --build
```

## Coding Style

- Backend: PEP 8 with ruff enforced
- Frontend: TypeScript strict mode, ESLint enforced
- Keep files small and focused (200-line maximum)

## Branch Naming

| Prefix | Use |
|---|---|
| `feature/` | New features |
| `fix/` | Bug fixes |
| `chore/` | Maintenance |
| `docs/` | Documentation |
| `ci/` | CI/CD changes |

Branch names use **kebab-case**. Never commit directly to `main`.

## PR Checklist

- [ ] Smoke check passes (lint + tests)
- [ ] Manual test completed for changed functionality
- [ ] Updated docs if behavior changed
- [ ] Follows Conventional Commits format
