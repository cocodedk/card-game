import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Modal from '../../src/components/Modal';

describe('Modal Component', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
    title: 'Test Modal',
    children: <div>Modal content</div>,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders when isOpen is true', () => {
    render(<Modal {...defaultProps} />);

    expect(screen.getByTestId('modal-overlay')).toBeInTheDocument();
    expect(screen.getByTestId('modal-title')).toHaveTextContent('Test Modal');
    expect(screen.getByTestId('modal-content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(<Modal {...defaultProps} isOpen={false} />);

    expect(screen.queryByTestId('modal-overlay')).not.toBeInTheDocument();
  });

  it('calls onClose when clicking the close button', () => {
    render(<Modal {...defaultProps} />);

    fireEvent.click(screen.getByTestId('modal-close'));
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('calls onClose when clicking the overlay', () => {
    render(<Modal {...defaultProps} />);

    fireEvent.click(screen.getByTestId('modal-overlay'));
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('calls onClose when pressing Escape key', () => {
    render(<Modal {...defaultProps} />);

    fireEvent.keyDown(document, { key: 'Escape' });
    expect(defaultProps.onClose).toHaveBeenCalled();
  });

  it('does not call onClose when pressing other keys', () => {
    render(<Modal {...defaultProps} />);

    fireEvent.keyDown(document, { key: 'Enter' });
    expect(defaultProps.onClose).not.toHaveBeenCalled();
  });

  it('has correct accessibility attributes', () => {
    render(<Modal {...defaultProps} />);

    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'modal-title');
  });
});
