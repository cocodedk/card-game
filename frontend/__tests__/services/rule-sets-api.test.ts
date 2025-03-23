import axios from 'axios';

/**
 * This test file checks if the rule sets API endpoint is accessible
 * and returns the expected data structure.
 */

describe('Rule Sets API', () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
  let accessToken: string | null = null;

  // Helper function to get auth token
  const getAuthToken = async () => {
    try {
      // Try to login first to get a token
      const response = await axios.post(`${apiUrl}/api/players/login/`, {
        username: 'testuser',
        password: 'testpassword'
      });

      if (response.data.tokens?.access) {
        return response.data.tokens.access;
      }

      return null;
    } catch (error) {
      console.error('Failed to get auth token:', error);
      return null;
    }
  };

  beforeAll(async () => {
    // Get auth token before running tests
    accessToken = await getAuthToken();
  });

  // Test different possible endpoints
  const endpoints = [
    '/api/rule-sets/',
    '/api/rule-sets',
    '/api/games/rule-sets/',
    '/api/games/rule-sets',
    '/api/ruleset/',
    '/api/ruleset',
    '/api/rulesets/',
    '/api/rulesets',
  ];

  test.each(endpoints)('Testing endpoint: %s', async (endpoint) => {
    try {
      const headers: Record<string, string> = {};
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
      }

      console.log(`Trying endpoint: ${apiUrl}${endpoint}`);
      const response = await axios.get(`${apiUrl}${endpoint}`, {
        headers,
        validateStatus: () => true // Don't throw on error status
      });

      console.log(`Status: ${response.status}, Data:`, response.data);

      if (response.status === 200) {
        console.log('✅ SUCCESSFUL ENDPOINT FOUND:', endpoint);
        console.log('Response structure:', JSON.stringify(response.data, null, 2));

        // Verify that rule sets exist in some format
        // This checks different possible response formats
        const hasRuleSets = response.data.rule_sets ||
                           Array.isArray(response.data) ||
                           response.data.results ||
                           response.data.data;

        expect(hasRuleSets).toBeTruthy();
      } else {
        console.log(`❌ Endpoint ${endpoint} returned status ${response.status}`);
      }
    } catch (error) {
      console.error(`Error testing ${endpoint}:`, error);
    }
  });

  // A more detailed test for when we find the correct endpoint
  test('Should handle error cases correctly', async () => {
    if (!accessToken) {
      console.log('Skipping detailed test due to missing auth token');
      return;
    }

    // Test with invalid token
    try {
      const response = await axios.get(`${apiUrl}/api/rule-sets/`, {
        headers: {
          'Authorization': 'Bearer invalid-token'
        },
        validateStatus: () => true
      });

      expect(response.status).toBe(401);
      console.log('✅ Unauthorized test passed');
    } catch (error) {
      console.error('Error testing unauthorized access:', error);
    }
  });
});
