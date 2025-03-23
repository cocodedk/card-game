import React from 'react';
import { render, screen, fireEvent, cleanup, act } from '@testing-library/react';
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

  afterEach(() => {
    cleanup();
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

  // New tests to enhance coverage
  it('properly cleans up event listeners when unmounted', () => {
    const { unmount } = render(<Modal {...defaultProps} />);

    // Add spy to document event listener removal
    const removeEventListenerSpy = jest.spyOn(document, 'removeEventListener');

    // Unmount the component
    unmount();

    // Check that the event listener was properly removed
    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function));

    // Clean up the spy
    removeEventListenerSpy.mockRestore();
  });

  it('prevents event propagation when clicking inside the modal', () => {
    const handleClose = jest.fn();
    const { container } = render(
      <Modal isOpen={true} onClose={handleClose} title="Test Modal">
        <div>Test Content</div>
      </Modal>
    );

    const modalContent = container.querySelector('.modal-content');
    const mockEvent = { stopPropagation: jest.fn() };

    if (modalContent) {
      fireEvent.click(modalContent, mockEvent);
      // Check that the event's stopPropagation was called
      expect(mockEvent.stopPropagation).toHaveBeenCalled();
    }
  });

  it('renders with custom content properly', () => {
    const customContent = (
      <div data-testid="custom-content">
        <button data-testid="custom-button">Custom Button</button>
        <input data-testid="custom-input" />
      </div>
    );

    render(<Modal {...defaultProps} children={customContent} />);

    expect(screen.getByTestId('custom-content')).toBeInTheDocument();
    expect(screen.getByTestId('custom-button')).toBeInTheDocument();
    expect(screen.getByTestId('custom-input')).toBeInTheDocument();
  });

  it('adds additional classes to modal when provided', () => {
    const handleClose = jest.fn();
    const { container } = render(
      <Modal
        isOpen={true}
        onClose={handleClose}
        title="Test Modal"
        className="custom-modal-class"
      >
        <div>Test Content</div>
      </Modal>
    );

    const modalDiv = container.querySelector('.modal.custom-modal-class');
    expect(modalDiv).not.toBeNull();
  });

  it('only listens for Escape key when modal is open', () => {
    const { rerender } = render(<Modal {...defaultProps} isOpen={false} />);

    // Modal is closed, pressing Escape should not call onClose
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(defaultProps.onClose).not.toHaveBeenCalled();

    // Rerender with modal open
    rerender(<Modal {...defaultProps} isOpen={true} />);

    // Modal is open, pressing Escape should call onClose
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(defaultProps.onClose).toHaveBeenCalled();
  });
});
