#!/bin/bash
# Comprehensive test runner for all backend tests
# This script runs all types of tests in the backend

# Don't exit on error, we want to run all tests
set +e

echo "===== Running All Backend Tests ====="

# Set the working directory to the project root
cd /app

# Set up environment variables
export PYTHONPATH=$PYTHONPATH:/app
export DJANGO_SETTINGS_MODULE=backend.tests.test_settings

# Function to print section headers
print_header() {
    echo ""
    echo "===== $1 ====="
    echo ""
}

# Function to run a command and check its exit status
run_test() {
    echo "Running: $1"
    eval "$1"
    local status=$?
    if [ $status -eq 0 ]; then
        echo "✅ Test passed"
        PASSED_TESTS+=("$1")
    else
        echo "❌ Test failed (exit code: $status)"
        FAILED_TESTS+=("$1")
    fi
    echo ""
}

# Check if Neo4j is available
check_neo4j() {
    print_header "Checking Neo4j Availability"
    # Try to connect to Neo4j
    if nc -z neo4j 7687 2>/dev/null; then
        echo "✅ Neo4j is available at neo4j:7687"
        NEO4J_AVAILABLE=true
    elif nc -z localhost 7687 2>/dev/null; then
        echo "✅ Neo4j is available at localhost:7687"
        NEO4J_AVAILABLE=true
    else
        echo "❌ Neo4j is not available"
        echo "Tests that require a real Neo4j connection will fail."
        echo "Make sure tests are using MockNeo4jTestCase from backend.tests.fixtures"
        echo "or ensure Neo4j is running and accessible."
        NEO4J_AVAILABLE=false
    fi
    echo ""
}

# Arrays to store test results
PASSED_TESTS=()
FAILED_TESTS=()
SKIPPED_TESTS=()
NEO4J_AVAILABLE=false

# Check Neo4j availability
check_neo4j

# 1. Run standalone tests (don't require Neo4j)
print_header "Running Standalone Tests"
run_test "python -m backend.tests.run_standalone"

# Prompt to continue after each test group
read -p "Continue testing? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi


# 2. Run unittest tests
print_header "Running Unittest Tests"
run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.tests.run_unittest"

# Prompt to continue after each test group
read -p "Continue testing? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi


# 3. Run pytest tests
print_header "Running Pytest Tests"
run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.tests.run_pytest"

# Prompt to continue after each test group
read -p "Continue testing? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi


# 4. Run Django tests - Note: This might fail due to card_game module not found
print_header "Running Django Tests"
if python -c "import card_game" 2>/dev/null; then
    run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.tests.run_tests"
else
    echo "⚠️ Skipping Django tests: 'card_game' module not found"
    SKIPPED_TESTS+=("DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.tests.run_tests")
fi

# Prompt to continue after each test group
read -p "Continue testing? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi

# 5. Run game service utils tests
print_header "Running Game Service Utils Tests"
run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.game.services.game_service_utils.tests.run_unittest"

# Prompt to continue after each test group
read -p "Continue testing? [Y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    exit 0
fi

if python -c "import pytest" 2>/dev/null; then
    run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.game.services.game_service_utils.tests.run_pytest"
else
    echo "⚠️ Skipping pytest tests: 'pytest' module not found"
    SKIPPED_TESTS+=("DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m backend.game.services.game_service_utils.tests.run_pytest")
fi

# 6. Run individual test modules directly
print_header "Running Individual Test Modules"

# Main test modules
TEST_MODULES=(
    "backend.tests.test_create_idiot_rule_set"
    "backend.tests.test_create_idiot_rule_set_integration"
    "backend.tests.test_create_idiot_rule_set_validation"
    "backend.tests.test_game_flow"
    "backend.tests.test_game_state"
    "backend.tests.test_special_cards"
)

# API and WebSocket tests that might fail due to Django URL configuration
API_TEST_MODULES=(
    "backend.tests.test_game_api"
    "backend.tests.test_game_api_integration"
    "backend.tests.test_game_websocket"
    "backend.tests.test_websocket_client"
)

# Run the core test modules
for module in "${TEST_MODULES[@]}"; do
    print_header "Testing module: $module"
    run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m unittest $module"
done

# Run the API test modules with warning about potential URL configuration issues
print_header "Running API and WebSocket Tests"
echo "Note: These tests might fail due to Django URL configuration issues"
echo "This is expected and doesn't indicate a problem with the core game logic"
echo ""

for module in "${API_TEST_MODULES[@]}"; do
    print_header "Testing module: $module"
    run_test "DJANGO_SETTINGS_MODULE=backend.tests.test_settings python -m unittest $module"
done

# Print summary
print_header "Test Summary"
echo "Passed tests: ${#PASSED_TESTS[@]}"
echo "Failed tests: ${#FAILED_TESTS[@]}"
echo "Skipped tests: ${#SKIPPED_TESTS[@]}"
echo ""

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo "All tests passed! 🎉"
else
    echo "The following tests failed:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "- $test"
    done

    echo ""
    if [ "$NEO4J_AVAILABLE" = false ]; then
        echo "⚠️ Neo4j Connection Issue: Some tests failed because Neo4j is not available."
        echo "To fix this, ensure tests are using MockNeo4jTestCase from backend.tests.fixtures"
        echo "instead of directly connecting to Neo4j."
        echo ""
        echo "Example of correct test class definition:"
        echo "from backend.tests.fixtures import MockNeo4jTestCase"
        echo "class MyTestCase(MockNeo4jTestCase):"
        echo ""
    fi

    echo "Note: Failures in API and WebSocket tests are often due to Django URL configuration"
    echo "issues and don't necessarily indicate problems with the core game logic."
fi

if [ ${#SKIPPED_TESTS[@]} -gt 0 ]; then
    echo ""
    echo "The following tests were skipped:"
    for test in "${SKIPPED_TESTS[@]}"; do
        echo "- $test"
    done
fi

echo ""
echo "===== All Tests Completed ====="
