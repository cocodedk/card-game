import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GameSetupForm from '../../src/components/GameSetupForm';
import '@testing-library/jest-dom';

describe('GameSetupForm', () => {
  const mockOnChange = jest.fn();
  const defaultSettings = {
    gameType: 'standard',
    maxPlayers: 4,
    timeLimit: 30,
    useAI: false,
    ruleSetId: 'rule1'
  };

  const mockRuleSets = [
    { id: 'rule1', name: 'Standard Rules', description: 'The standard rule set for the game', version: '1.0' },
    { id: 'rule2', name: 'Quick Play', description: 'A faster variant with simplified rules', version: '1.1' },
    { id: 'rule3', name: 'Advanced', description: 'Complex rules for experienced players', version: '2.0' }
  ];

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  test('renders form with all fields when rule sets are loaded', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    expect(screen.getByTestId('game-setup-form')).toBeInTheDocument();
    expect(screen.getByTestId('rule-set-select')).toBeInTheDocument();
    expect(screen.getByTestId('game-type-select')).toBeInTheDocument();
    expect(screen.getByTestId('max-players-select')).toBeInTheDocument();
    expect(screen.getByTestId('time-limit-input')).toBeInTheDocument();
    expect(screen.getByTestId('use-ai-checkbox')).toBeInTheDocument();

    // Rule set description should be visible when a rule is selected
    expect(screen.getByTestId('rule-set-description')).toBeInTheDocument();
    expect(screen.getByText('The standard rule set for the game')).toBeInTheDocument();
  });

  test('shows loading state for rule sets', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={[]}
        loadingRuleSets={true}
      />
    );

    expect(screen.getByTestId('rule-sets-loading')).toBeInTheDocument();
    expect(screen.queryByTestId('rule-set-select')).not.toBeInTheDocument();
  });

  test('shows "No rule sets available" when ruleSets array is empty', () => {
    render(
      <GameSetupForm
        settings={{...defaultSettings, ruleSetId: ''}}
        onChange={mockOnChange}
        ruleSets={[]}
        loadingRuleSets={false}
      />
    );

    expect(screen.getByTestId('rule-set-select')).toBeInTheDocument();
    expect(screen.getByText('No rule sets available')).toBeInTheDocument();
  });

  test('calls onChange with correct value when game type is changed', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const gameTypeSelect = screen.getByTestId('game-type-select');
    fireEvent.change(gameTypeSelect, { target: { name: 'gameType', value: 'quick' } });

    expect(mockOnChange).toHaveBeenCalledWith({ gameType: 'quick' });
  });

  test('calls onChange with correct value when max players is changed', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const maxPlayersSelect = screen.getByTestId('max-players-select');
    fireEvent.change(maxPlayersSelect, { target: { name: 'maxPlayers', value: '6' } });

    expect(mockOnChange).toHaveBeenCalledWith({ maxPlayers: '6' });
  });

  test('calls onChange with correct value when time limit is changed', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const timeLimitInput = screen.getByTestId('time-limit-input');
    fireEvent.change(timeLimitInput, { target: { value: '60' } });

    expect(mockOnChange).toHaveBeenCalledWith({ timeLimit: 60 });
  });

  test('enforces time limit constraints', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const timeLimitInput = screen.getByTestId('time-limit-input');

    // Test below minimum (should set to 5)
    fireEvent.change(timeLimitInput, { target: { value: '3' } });
    expect(mockOnChange).toHaveBeenCalledWith({ timeLimit: 5 });

    mockOnChange.mockClear();

    // Test above maximum (should set to 120)
    fireEvent.change(timeLimitInput, { target: { value: '150' } });
    expect(mockOnChange).toHaveBeenCalledWith({ timeLimit: 120 });

    mockOnChange.mockClear();

    // Test 0 for no limit (should accept 0)
    fireEvent.change(timeLimitInput, { target: { value: '0' } });
    expect(mockOnChange).toHaveBeenCalledWith({ timeLimit: 0 });
  });

  test('calls onChange with correct value when AI inclusion is toggled', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const useAICheckbox = screen.getByTestId('use-ai-checkbox');
    fireEvent.click(useAICheckbox);

    expect(mockOnChange).toHaveBeenCalledWith({ useAI: true });
  });

  test('calls onChange with correct value when rule set is changed', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    const ruleSetSelect = screen.getByTestId('rule-set-select');
    fireEvent.change(ruleSetSelect, { target: { name: 'ruleSetId', value: 'rule2' } });

    expect(mockOnChange).toHaveBeenCalledWith({ ruleSetId: 'rule2' });
  });

  test('displays tournament info when tournament game type is selected', () => {
    render(
      <GameSetupForm
        settings={{...defaultSettings, gameType: 'tournament'}}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    expect(screen.getByTestId('tournament-info')).toBeInTheDocument();
    expect(screen.getByText(/Tournament mode will create multiple rounds of games/)).toBeInTheDocument();
  });

  test('does not display tournament info when non-tournament game type is selected', () => {
    render(
      <GameSetupForm
        settings={defaultSettings}
        onChange={mockOnChange}
        ruleSets={mockRuleSets}
        loadingRuleSets={false}
      />
    );

    expect(screen.queryByTestId('tournament-info')).not.toBeInTheDocument();
  });
});
