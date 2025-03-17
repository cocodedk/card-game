import { render, screen } from '@testing-library/react';
import Home from '../src/pages/index';
import '@testing-library/jest-dom';
import { describe, it, expect } from '@jest/globals';

describe('Home', () => {
  it('renders without crashing', () => {
    render(<Home />);
    expect(screen).toBeTruthy();
  });
});
