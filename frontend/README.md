# Card Game Frontend

A Next.js TypeScript frontend for the card game application.

## Tech Stack

- Next.js 14
- TypeScript
- React Query
- Zustand
- Tailwind CSS
- Socket.io Client
- Jest & React Testing Library

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run linting
npm run lint
```

## Project Structure

```
/app/frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Next.js pages and API routes
│   ├── hooks/         # Custom React hooks
│   ├── stores/        # Zustand state management
│   ├── types/         # TypeScript type definitions
│   └── utils/         # Helper functions and utilities
├── public/            # Static assets
└── __tests__/         # Test files
```

## Testing

Tests are written using Jest and React Testing Library. Test files are located in the `__tests__` directory and follow the naming convention `*.test.tsx`.

### Testing Guidelines

- Write tests for all new components and features
- Follow the React Testing Library guiding principles
- Test user interactions and component behavior
- Mock external dependencies and API calls
- Ensure proper error handling is tested
