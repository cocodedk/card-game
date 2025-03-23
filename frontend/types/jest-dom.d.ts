// Import the types
import '@testing-library/jest-dom';

// Extend the Jest matchers
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toHaveAttribute(attr: string, value?: string): R;
      toHaveTextContent(text: string | RegExp): R;
      toHaveClass(className: string): R;
      toBeVisible(): R;
      toBeDisabled(): R;
      toBeEnabled(): R;
      toHaveValue(value: string | number | string[]): R;
      toHaveFocus(): R;
      toBeChecked(): R;
      toContainElement(element: HTMLElement | null): R;
      toContainHTML(html: string): R;
      toHaveStyle(css: Record<string, any>): R;
      toHaveBeenCalled(): R;
      toHaveBeenCalledTimes(times: number): R;
      toHaveBeenCalledWith(...args: any[]): R;
      toHaveBeenLastCalledWith(...args: any[]): R;
    }
  }
}

export {};
