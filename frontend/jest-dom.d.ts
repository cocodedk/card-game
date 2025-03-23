// jest-dom.d.ts
import '@testing-library/jest-dom';

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeInTheDocument(): R;
      toHaveTextContent(text: string | RegExp): R;
      toHaveAttribute(attr: string, value?: string): R;
      toHaveClass(className: string): R;
      toBeVisible(): R;
      toBeDisabled(): R;
      toBeEnabled(): R;
      toBeChecked(): R;
      toBeFocused(): R;
      toBeEmpty(): R;
      toBeInvalid(): R;
      toBeRequired(): R;
      toBeValid(): R;
      toHaveStyle(css: string): R;
      toHaveValue(value: string | string[] | number): R;
      toContainElement(element: HTMLElement | null): R;
      toContainHTML(html: string): R;
      toHaveDescription(text: string | RegExp): R;
      toHaveDisplayValue(value: string | RegExp | Array<string | RegExp>): R;
      toHaveAccessibleDescription(text: string | RegExp): R;
      toHaveAccessibleName(text: string | RegExp): R;
      toHaveFormValues(expectedValues: Record<string, any>): R;

      // Standard Jest matchers
      toBe(expected: any): R;
      toBeDefined(): R;
      toBeFalsy(): R;
      toBeNull(): R;
      toBeTruthy(): R;
      toBeUndefined(): R;
      toEqual(expected: any): R;
      toContain(item: any): R;
      toHaveLength(length: number): R;
      toHaveBeenCalled(): R;
      toHaveBeenCalledTimes(times: number): R;
      toHaveBeenCalledWith(...args: any[]): R;
      toHaveBeenLastCalledWith(...args: any[]): R;
      toHaveBeenNthCalledWith(nthCall: number, ...args: any[]): R;
      toMatch(pattern: any): R;
      toMatchObject(object: any): R;
      toThrow(error?: any): R;
    }
  }

  // Add missing declarations for Jest mock functions
  interface MockInstance<T extends (...args: any[]) => any> extends Function {
    mockClear(): this;
    mockReset(): this;
    mockRestore(): void;
    mockImplementation(fn: T): this;
    mockImplementationOnce(fn: T): this;
    mockReturnThis(): this;
    mockReturnValue(value: ReturnType<T>): this;
    mockReturnValueOnce(value: ReturnType<T>): this;
    mockResolvedValue<U extends Promise<any>>(value: Awaited<U>): this;
    mockResolvedValueOnce<U extends Promise<any>>(value: Awaited<U>): this;
    mockRejectedValue(value: any): this;
    mockRejectedValueOnce(value: any): this;
    getMockName(): string;
    mockName(name: string): this;
    mock: {
      calls: any[][];
      results: { type: 'return' | 'throw'; value: any }[];
      instances: any[];
      contexts: any[];
      lastCall: any[];
    };
  }

  interface JestMockFn<T extends (...args: any[]) => any> extends MockInstance<T> {}
}

export {};
