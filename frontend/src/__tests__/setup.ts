import "@testing-library/jest-dom";

// jsdom doesn't implement ResizeObserver (used by Recharts)
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};
