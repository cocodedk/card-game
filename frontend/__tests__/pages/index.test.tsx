import React from 'react';
import { render, screen } from '@testing-library/react';
import HomePage from '../../src/pages/index';

// Mock the AuthLayout component
jest.mock('../../src/components/AuthLayout', () => {
  return {
    __esModule: true,
    default: ({ children, title, description }: any) => (
      <div data-testid="auth-layout">
        <h1 data-testid="page-title">{title}</h1>
        <p data-testid="page-description">{description}</p>
        <div data-testid="auth-layout-content">{children}</div>
      </div>
    ),
  };
});

// Mock Next.js Link component
jest.mock('next/link', () => {
  return {
    __esModule: true,
    default: ({ href, children, className }: any) => (
      <a href={href} className={className} data-testid={`link-to-${href.replace('/', '')}`}>
        {children}
      </a>
    ),
  };
});

describe('HomePage', () => {
  test('renders with correct title and description', () => {
    render(<HomePage />);

    // Check if AuthLayout receives correct props
    const title = screen.getByTestId('page-title');
    const description = screen.getByTestId('page-description');

    expect(title).toBeInTheDocument();
    expect(title.textContent).toBe('Welcome to Card Game');

    expect(description).toBeInTheDocument();
    expect(description.textContent).toBe('A strategic card game where your decisions matter');
  });

  test('renders hero section with call-to-action buttons', () => {
    render(<HomePage />);

    // Check if hero section exists
    const heroHeading = screen.getByText('Start Your Card Game Journey');
    expect(heroHeading).toBeInTheDocument();

    // Check if call-to-action buttons exist and point to correct routes
    const createAccountLinks = screen.getAllByTestId('link-to-register');
    // The first link is in the hero section
    const createAccountLink = createAccountLinks[0];
    const signInLink = screen.getByTestId('link-to-login');

    expect(createAccountLink).toBeInTheDocument();
    expect(createAccountLink.getAttribute('href')).toBe('/register');
    expect(createAccountLink.textContent).toBe('Create Account');

    expect(signInLink).toBeInTheDocument();
    expect(signInLink.getAttribute('href')).toBe('/login');
    expect(signInLink.textContent).toBe('Sign In');
  });

  test('renders feature section with three features', () => {
    render(<HomePage />);

    // Check if feature headings exist
    const collectCardsHeading = screen.getByText('Collect Cards');
    const buildDecksHeading = screen.getByText('Build Decks');
    const battlePlayersHeading = screen.getByText('Battle Players');

    expect(collectCardsHeading).toBeInTheDocument();
    expect(buildDecksHeading).toBeInTheDocument();
    expect(battlePlayersHeading).toBeInTheDocument();

    // Check if feature descriptions exist
    const collectCardsDescription = screen.getByText(/Build your collection with hundreds of unique cards/);
    const buildDecksDescription = screen.getByText(/Create powerful deck combinations/);
    const battlePlayersDescription = screen.getByText(/Challenge other players in real-time matches/);

    expect(collectCardsDescription).toBeInTheDocument();
    expect(buildDecksDescription).toBeInTheDocument();
    expect(battlePlayersDescription).toBeInTheDocument();
  });

  test('renders bottom call-to-action section', () => {
    render(<HomePage />);

    // Check if CTA section exists
    const ctaHeading = screen.getByText('Ready to Play?');
    expect(ctaHeading).toBeInTheDocument();

    // Check if CTA link exists and points to correct route
    const registerLinks = screen.getAllByTestId('link-to-register');
    // The second link is in the bottom CTA section
    const getStartedLink = registerLinks[1];

    expect(getStartedLink).toBeInTheDocument();
    expect(getStartedLink.getAttribute('href')).toBe('/register');
    expect(getStartedLink.textContent).toBe('Get Started');
  });
});
