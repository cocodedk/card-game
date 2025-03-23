import React from 'react';
import { render, screen } from '@testing-library/react';
import AuthLayout from '../../src/components/AuthLayout';
import '@testing-library/jest-dom';

// Mock Next.js components
jest.mock('next/head', () => {
  return {
    __esModule: true,
    default: ({ children }: { children: React.ReactNode }) => {
      return <div data-testid="mock-head">{children}</div>;
    },
  };
});

jest.mock('next/link', () => {
  return {
    __esModule: true,
    default: ({ href, children, className }: { href: string; children: React.ReactNode; className?: string }) => {
      return (
        <a href={href} className={className} data-testid={`link-to-${href}`}>
          {children}
        </a>
      );
    },
  };
});

jest.mock('next/image', () => {
  return {
    __esModule: true,
    default: ({ src, alt, width, height }: { src: string; alt: string; width: number; height: number }) => {
      return <img src={src} alt={alt} width={width} height={height} data-testid="mock-image" />;
    },
  };
});

describe('AuthLayout', () => {
  test('renders with default props', () => {
    render(
      <AuthLayout title="Test Title">
        <div data-testid="test-content">Test Content</div>
      </AuthLayout>
    );

    // Check title
    expect(screen.getByText('Test Title')).toBeInTheDocument();

    // Check description (default)
    expect(screen.getByText('Welcome to the Card Game')).toBeInTheDocument();

    // Check links - use getAllByTestId for home link since there are two of them
    const homeLinks = screen.getAllByTestId('link-to-/');
    expect(homeLinks.length).toBeGreaterThan(0);
    expect(screen.getByTestId('link-to-/login')).toBeInTheDocument();
    expect(screen.getByTestId('link-to-/register')).toBeInTheDocument();

    // Check child content
    expect(screen.getByTestId('test-content')).toBeInTheDocument();
    expect(screen.getByText('Test Content')).toBeInTheDocument();

    // Check footer
    expect(screen.getByText(/Card Game. All rights reserved./)).toBeInTheDocument();
    const currentYear = new Date().getFullYear().toString();
    expect(screen.getByText(new RegExp(`©\\s*${currentYear}\\s+Card Game`, 'i'))).toBeInTheDocument();
  });

  test('renders with custom props', () => {
    render(
      <AuthLayout
        title="Custom Title"
        description="Custom description for the page"
        showLoginLink={false}
        showRegisterLink={true}
      >
        <div data-testid="custom-content">Custom Child Content</div>
      </AuthLayout>
    );

    // Check title
    expect(screen.getByText('Custom Title')).toBeInTheDocument();

    // Check custom description
    expect(screen.getByText('Custom description for the page')).toBeInTheDocument();

    // Check links - login should be hidden, use getAllByTestId for home link
    const homeLinks = screen.getAllByTestId('link-to-/');
    expect(homeLinks.length).toBeGreaterThan(0);
    expect(screen.queryByTestId('link-to-/login')).not.toBeInTheDocument();
    expect(screen.getByTestId('link-to-/register')).toBeInTheDocument();

    // Check child content
    expect(screen.getByTestId('custom-content')).toBeInTheDocument();
    expect(screen.getByText('Custom Child Content')).toBeInTheDocument();
  });

  test('hides register link when showRegisterLink is false', () => {
    render(
      <AuthLayout
        title="No Register"
        showLoginLink={true}
        showRegisterLink={false}
      >
        <div>Content</div>
      </AuthLayout>
    );

    // Check links - register should be hidden, use getAllByTestId for home link
    const homeLinks = screen.getAllByTestId('link-to-/');
    expect(homeLinks.length).toBeGreaterThan(0);
    expect(screen.getByTestId('link-to-/login')).toBeInTheDocument();
    expect(screen.queryByTestId('link-to-/register')).not.toBeInTheDocument();
  });

  test('hides both login and register links', () => {
    render(
      <AuthLayout
        title="Authenticated View"
        showLoginLink={false}
        showRegisterLink={false}
      >
        <div>Authenticated Content</div>
      </AuthLayout>
    );

    // Check links - both login and register should be hidden, use getAllByTestId for home link
    const homeLinks = screen.getAllByTestId('link-to-/');
    expect(homeLinks.length).toBeGreaterThan(0); // Home link still visible
    expect(screen.queryByTestId('link-to-/login')).not.toBeInTheDocument();
    expect(screen.queryByTestId('link-to-/register')).not.toBeInTheDocument();
  });

  test('renders with no description when not provided', () => {
    render(
      <AuthLayout
        title="No Description"
        description=""
      >
        <div>Content</div>
      </AuthLayout>
    );

    // Default description should not be shown
    expect(screen.queryByText('Welcome to the Card Game')).not.toBeInTheDocument();
  });

  test('sets document title correctly', () => {
    render(
      <AuthLayout title="Page Title">
        <div>Content</div>
      </AuthLayout>
    );

    // Check for title tag in the mocked head
    const headElement = screen.getByTestId('mock-head');
    expect(headElement).toHaveTextContent('Page Title - Card Game');
  });
});
