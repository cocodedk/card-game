# Multiplayer Card Game

A modern multiplayer card game with authentication, real-time gameplay, and progressive design.

## Technology Stack

### Backend
- Django 5.0: Web framework
- Django REST Framework 3.14: API endpoints
- Django Channels 4.0: WebSocket support
- Daphne 4.0: ASGI server for Django
- Neo4j 5.16 with Neomodel 5.2: Graph database
- JWT: Authentication
- Watchdog 3.0: Automatic reloading in development

### Frontend
- Next.js 14.1: React framework with SSR
- TypeScript 5.3: Type-safe JavaScript
- Tailwind CSS 3.4: Utility-first styling
- TanStack Query 5.18: Data fetching and caching
- Socket.io Client 4.7: Real-time communication

### Infrastructure
- Docker: Containerization
- Redis 7.2: WebSocket message broker
- Neo4j 5.16: Graph database
- Node.js 20: JavaScript runtime
- Python 3.12: Backend runtime

## Features

- User authentication and profiles
- Real-time multiplayer gameplay
- Customizable decks and cards
- Game history and statistics
- Responsive design for all devices

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)

### Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/card-game.git
   cd card-game
   ```

2. Start the development environment with Docker Compose:
   ```
   docker-compose up
   ```

3. Access the applications:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Neo4j Browser: http://localhost:7474

### Manual Setup (without Docker)

#### Backend
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the development server with Daphne and Watchdog:
   ```
   watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- daphne -b 0.0.0.0 -p 8000 card_game.asgi:application
   ```

#### Frontend
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm run dev
   ```

## Project Structure

```
card-game/
├── backend/               # Django backend
│   ├── authentication/    # Authentication app
│   ├── game/              # Game logic and API
│   ├── api/               # API endpoints
│   └── card_game/         # Django project settings
├── frontend/              # Next.js frontend
│   ├── public/            # Static assets
│   └── src/               # Source code
│       ├── components/    # React components
│       ├── pages/         # Next.js pages
│       ├── styles/        # CSS styles
│       └── utils/         # Utility functions
└── docker/                # Docker configuration
```

## Game Rules

The game rules are implemented on the server-side to ensure consistency and prevent cheating. The rule system is designed to be modular and configurable, allowing for future updates and changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
