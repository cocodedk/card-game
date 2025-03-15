# Backend Tests

This directory contains tests for the backend of the Idiot Card Game application.

## Test Organization

The tests are organized into the following categories:

### Unit Tests

- `test_create_idiot_rule_set.py`: Tests for creating rule sets for the Idiot Card Game
- `test_create_idiot_rule_set_validation.py`: Tests for validating rule set parameters
- `test_game_state.py`: Tests for the GameState model and game flow functionality
- `test_game_api.py`: Tests for the game API endpoints
- `test_game_websocket.py`: Tests for WebSocket notifications

### Integration Tests

- `test_create_idiot_rule_set_integration.py`: Integration tests for rule set creation
- `test_game_api_integration.py`: Integration tests for game API endpoints
- `test_game_flow.py`: Tests for game flow functionality

## Running Tests

To run all tests:

```bash
cd /app
DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.tests.run_unittest
```

To run a specific test file:

```bash
cd /app
DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m unittest backend.tests.test_game_state
```

## Test Fixtures

The `fixtures.py` file contains fixtures for setting up the test environment, including:

- `Neo4jTestCase`: Base test case for tests that require Neo4j
- `MockNeo4jTestCase`: Base test case for tests that should mock Neo4j

## Test Coverage

The tests cover the following functionality:

- **Rule Set Creation**: Creating and validating rule sets for the Idiot Card Game
- **Game State Management**: Managing the state of a game, including player hands, card piles, and game flow
- **API Endpoints**: Testing the API endpoints for creating games, playing cards, and getting game state
- **WebSocket Notifications**: Testing real-time notifications for game events
- **Full Game Flow**: Testing a complete game flow from start to finish

## Adding New Tests

When adding new tests, follow these guidelines:

1. Use `MockNeo4jTestCase` as the base class for tests that don't need a real Neo4j database
2. Mock external dependencies using the `patch` decorator
3. Use descriptive test method names that clearly indicate what is being tested
4. Include assertions that verify the expected behavior
5. Add comments to explain complex test logic

## Troubleshooting

If you encounter issues with the tests:

1. Make sure the Django settings module is set correctly:
   ```bash
   export DJANGO_SETTINGS_MODULE=backend.tests.test_settings
   ```

2. Check that the Neo4j connection is configured correctly in `test_settings.py`

3. Ensure that all required dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

4. If you're getting errors about missing modules, make sure the Python path includes the project root:
   ```bash
   export PYTHONPATH=$PYTHONPATH:/app
   ```
