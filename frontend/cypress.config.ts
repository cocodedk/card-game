import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      return config;
    },
    baseUrl: 'http://localhost:3001',
    env: {
      API_URL: 'http://backend:8000/api',
      WS_URL: 'ws://backend:8000/ws',
    },
    defaultCommandTimeout: 10000,
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: false,
    retries: {
      runMode: 2,
      openMode: 0,
    },
  },
});
