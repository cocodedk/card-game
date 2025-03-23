import React, { useEffect } from 'react';
import { ModalProps } from '../types/game';

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className = '' }) => {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      data-testid="modal-overlay"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className="fixed inset-0 bg-black opacity-50" />
      <div
        className={`modal relative bg-white rounded-lg shadow-xl p-6 w-96 max-w-full mx-4 ${className}`.trim()}
        onClick={e => e.stopPropagation()}
      >
        <button
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          onClick={onClose}
          data-testid="modal-close"
          aria-label="Close modal"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <h2
          id="modal-title"
          className="text-xl font-semibold mb-4"
          data-testid="modal-title"
        >
          {title}
        </h2>
        <div className="mt-2" data-testid="modal-content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Modal;
