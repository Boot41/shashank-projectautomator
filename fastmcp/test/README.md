# FastMCP Test Suite

This directory contains comprehensive tests for the FastMCP project, designed to achieve maximum code coverage and ensure reliability.

## Test Structure

```
test/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── pytest.ini                 # Pytest settings
├── requirements-test.txt       # Test dependencies
├── run_tests.py               # Test runner script
├── README.md                  # This file
├── unit/                      # Unit tests
│   ├── test_github_service.py
│   ├── test_jira_service.py
│   ├── test_ai_service.py
│   ├── test_context_service.py
│   ├── test_email_service.py
│   ├── test_models.py
│   ├── test_coordinator.py
│   └── test_tool_runners.py
├── integration/               # Integration tests
│   └── test_main_endpoints.py
└── fixtures/                  # Test fixtures and mock data
```

## Test Categories

### Unit Tests (`test/unit/`)

- **`test_github_service.py`**: Tests for GitHub API service functions
- **`test_jira_service.py`**: Tests for Jira API service functions
- **`test_ai_service.py`**: Tests for AI service functions
- **`test_context_service.py`**: Tests for context management service
- **`test_email_service.py`**: Tests for email service functions
- **`test_models.py`**: Tests for Pydantic models
- **`test_coordinator.py`**: Tests for the main coordinator logic
- **`test_tool_runners.py`**: Tests for tool runner functions

### Integration Tests (`test/integration/`)

- **`test_main_endpoints.py`**: Tests for FastAPI endpoints

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
python test/run_tests.py install
```

### Test Commands

#### Run All Tests
```bash
python test/run_tests.py all
```

#### Run Unit Tests Only
```bash
python test/run_tests.py unit
```

#### Run Integration Tests Only
```bash
python test/run_tests.py integration
```

#### Run Tests with Coverage
```bash
python test/run_tests.py coverage
```

#### Run Specific Test File
```bash
python test/run_tests.py specific --test-path unit/test_github_service.py
```

#### Run Code Quality Checks
```bash
# Linting
python test/run_tests.py lint

# Formatting
python test/run_tests.py format

# Import sorting
python test/run_tests.py sort
```

### Direct Pytest Commands

You can also run tests directly with pytest:

```bash
# Run all tests
pytest test/ -v

# Run with coverage
pytest test/ --cov=app --cov-report=html

# Run specific test file
pytest test/unit/test_github_service.py -v

# Run tests by marker
pytest test/ -m unit
pytest test/ -m integration
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- **Coverage threshold**: 70%
- **Branch coverage**: Enabled
- **Async mode**: Auto
- **Markers**: `unit`, `integration`, `slow`, `mock`

### Test Fixtures (`conftest.py`)

The test suite includes comprehensive fixtures for:

- **Mock settings**: Simulated configuration for testing
- **Mock HTTP client**: Simulated HTTP requests
- **Mock AI service**: Simulated AI responses
- **Sample data**: Predefined test data for GitHub, Jira, etc.
- **Temporary directories**: For file system tests

## Test Coverage Goals

The test suite is designed to achieve:

- **Overall coverage**: 70%+ (configurable threshold)
- **Branch coverage**: 70%+ (configurable threshold)
- **Service coverage**: 80%+ for critical services
- **Model coverage**: 90%+ for data models

## Test Strategy

### Mocking Strategy

1. **External APIs**: All external API calls are mocked
2. **File System**: File operations use temporary directories
3. **Network**: HTTP requests are mocked with realistic responses
4. **AI Services**: AI responses are mocked with predictable outputs

### Test Data

- **Realistic data**: Test data mimics real API responses
- **Edge cases**: Tests include boundary conditions and error cases
- **Special characters**: Tests include Unicode and special characters
- **Large data**: Tests include performance with large datasets

### Error Handling

- **API errors**: Tests cover various HTTP error scenarios
- **Network timeouts**: Tests include timeout handling
- **Invalid data**: Tests cover malformed input handling
- **Authentication**: Tests cover authentication failures

## Continuous Integration

The test suite is designed to run in CI/CD environments:

- **Fast execution**: Tests complete within reasonable time limits
- **Deterministic**: Tests produce consistent results
- **Isolated**: Tests don't depend on external services
- **Parallel execution**: Tests can run in parallel when possible

## Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Real-time coverage display
- **HTML**: Detailed HTML report in `htmlcov/` directory
- **XML**: Machine-readable coverage data

## Best Practices

### Writing Tests

1. **Descriptive names**: Test names clearly describe what is being tested
2. **Single responsibility**: Each test focuses on one specific behavior
3. **Arrange-Act-Assert**: Tests follow the AAA pattern
4. **Mock external dependencies**: Use mocks for external services
5. **Test edge cases**: Include boundary conditions and error scenarios

### Test Organization

1. **Group related tests**: Use test classes for related functionality
2. **Use fixtures**: Leverage pytest fixtures for common setup
3. **Mark tests**: Use pytest markers for test categorization
4. **Keep tests independent**: Tests should not depend on each other

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the project root is in Python path
2. **Mock failures**: Check that mocks are properly configured
3. **Async issues**: Ensure async tests use `@pytest.mark.asyncio`
4. **Coverage issues**: Check that all code paths are tested

### Debug Mode

Run tests with verbose output for debugging:

```bash
pytest test/ -v -s --tb=long
```

### Test Discovery

If tests are not being discovered:

```bash
pytest test/ --collect-only
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Add appropriate markers (`@pytest.mark.unit` or `@pytest.mark.integration`)
3. Include both success and error cases
4. Update this README if adding new test categories
5. Ensure tests pass before submitting

## Performance

The test suite is optimized for performance:

- **Parallel execution**: Use `pytest-xdist` for parallel test runs
- **Selective testing**: Run only relevant tests during development
- **Fast feedback**: Quick test execution for rapid development cycles
- **Resource management**: Tests clean up after themselves
