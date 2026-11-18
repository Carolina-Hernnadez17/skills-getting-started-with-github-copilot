# Testing Plan for Mergington High School API

## Overview
This document outlines the testing strategy for the FastAPI backend application.

---

## Project Structure

```
skills-getting-started-with-github-copilot/
├── src/
│   ├── app.py              # Main FastAPI application
│   └── static/             # Frontend files
├── tests/                  # NEW: Test directory
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures and configuration
│   ├── test_endpoints.py   # Endpoint tests
│   ├── test_signup.py      # Signup flow tests
│   └── test_unregister.py  # Unregister flow tests
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Dependencies
└── ...
```

---

## Testing Strategy

### Framework & Tools
- **Framework**: pytest (already in requirements.txt)
- **HTTP Client**: httpx (already in requirements.txt)
- **Test Runner**: pytest
- **Pattern**: AAA (Arrange-Act-Assert)

### AAA Pattern (Arrange-Act-Assert)

Each test follows a clear three-part structure:

```python
def test_example():
    # ARRANGE: Set up test data and preconditions
    client = TestClient(app)
    email = "test@example.com"
    activity = "Chess Club"
    
    # ACT: Execute the code being tested
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # ASSERT: Verify the results
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
```

**Benefits:**
- Clear, predictable structure
- Easy to understand test intent
- Separates setup, execution, and verification
- Makes failures easier to diagnose

### Test Categories

#### 1. **API Endpoints Tests** (`test_endpoints.py`)
Tests basic API functionality and responses.

| Test | Endpoint | Expected Behavior |
|------|----------|-------------------|
| `test_root_redirect` | GET / | Redirects to /static/index.html |
| `test_get_activities` | GET /activities | Returns all activities with correct structure |
| `test_get_activities_contains_required_fields` | GET /activities | Each activity has description, schedule, max_participants, participants |

**Example Test Structure (AAA Pattern):**
```python
def test_get_activities():
    # ARRANGE
    client = TestClient(app)
    
    # ACT
    response = client.get("/activities")
    
    # ASSERT
    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "max_participants" in activities["Chess Club"]
    assert "participants" in activities["Chess Club"]
```

#### 2. **Signup Flow Tests** (`test_signup.py`)
Tests participant registration functionality and validation.

| Test | Scenario | Expected Behavior |
|------|----------|-------------------|
| `test_signup_new_participant` | Valid email, existing activity | Participant added to list, 200 status |
| `test_signup_duplicate_participant` | Email already signed up | Returns 400 error, participant not duplicated |
| `test_signup_nonexistent_activity` | Activity doesn't exist | Returns 404 error |
| `test_signup_updates_count` | After signup | Participant count increases |
| `test_signup_max_capacity_check` | Future: validate max capacity | Should prevent signup if full |

**Example Test Structure (AAA Pattern):**
```python
def test_signup_new_participant():
    # ARRANGE
    client = TestClient(app)
    email = "new@example.com"
    activity = "Chess Club"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # ACT
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert signup_response.status_code == 200
    assert "Signed up" in signup_response.json()["message"]
    
    # Verify participant was added
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity]["participants"])
    assert final_count == initial_count + 1
    assert email in final_response.json()[activity]["participants"]


def test_signup_duplicate_participant():
    # ARRANGE
    client = TestClient(app)
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # ACT
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()
```

#### 3. **Unregister Flow Tests** (`test_unregister.py`)
Tests participant removal functionality.

| Test | Scenario | Expected Behavior |
|------|----------|-------------------|
| `test_unregister_existing_participant` | Participant exists | Removed from list, 200 status |
| `test_unregister_nonexistent_participant` | Participant not in activity | Returns 404 error |
| `test_unregister_nonexistent_activity` | Activity doesn't exist | Returns 404 error |
| `test_unregister_updates_count` | After unregister | Participant count decreases |

**Example Test Structure (AAA Pattern):**
```python
def test_unregister_existing_participant():
    # ARRANGE
    client = TestClient(app)
    email = "michael@mergington.edu"  # Already in Chess Club
    activity = "Chess Club"
    
    # Get initial participant count
    initial_response = client.get("/activities")
    initial_count = len(initial_response.json()[activity]["participants"])
    
    # ACT
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    # ASSERT
    assert unregister_response.status_code == 200
    assert "Unregistered" in unregister_response.json()["message"]
    
    # Verify participant was removed
    final_response = client.get("/activities")
    final_count = len(final_response.json()[activity]["participants"])
    assert final_count == initial_count - 1
    assert email not in final_response.json()[activity]["participants"]


def test_unregister_nonexistent_participant():
    # ARRANGE
    client = TestClient(app)
    email = "nonexistent@example.com"
    activity = "Chess Club"
    
    # ACT
    response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

#### 4. **Data Integrity Tests** (`test_endpoints.py`)
Tests data consistency across operations.

| Test | Scenario | Expected Behavior |
|------|----------|-------------------|
| `test_participant_count_accuracy` | Signup then unregister | Counts remain accurate |
| `test_activities_state_isolation` | Modify one activity | Other activities unaffected |

---

## Test Fixtures

### `conftest.py` - Shared Fixtures

Using fixtures to set up reusable test data following the AAA pattern:

```python
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    ARRANGE: Provides a TestClient for making requests
    Yields the client for use in tests
    """
    test_client = TestClient(app)
    yield test_client
    # Teardown: Can reset state here if needed


@pytest.fixture
def sample_activity():
    """
    ARRANGE: Provides a known activity name for testing
    """
    return "Chess Club"


@pytest.fixture
def sample_email():
    """
    ARRANGE: Provides a test email that doesn't already exist
    """
    return "newtester@example.com"


@pytest.fixture
def existing_participant():
    """
    ARRANGE: Provides an email that's already registered
    """
    return "michael@mergington.edu"
```

### Using Fixtures in Tests

```python
def test_signup_with_fixture(client, sample_activity, sample_email):
    # ARRANGE (fixtures already set up)
    
    # ACT
    response = client.post(
        f"/activities/{sample_activity}/signup",
        params={"email": sample_email}
    )
    
    # ASSERT
    assert response.status_code == 200
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_signup.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_signup.py::test_signup_new_participant

# Run with coverage
pytest --cov=src tests/
```

---

## Coverage Goals

- **Target**: Minimum 80% code coverage
- **Focus Areas**:
  - All endpoint handlers
  - Error cases (404, 400 responses)
  - Data mutation operations (signup, unregister)

---

## Implementation Priority

### Phase 1 (High Priority)
- [ ] Set up `conftest.py` with TestClient fixture
- [ ] Create `test_endpoints.py` with basic endpoint tests
- [ ] Create `test_signup.py` with signup validation tests
- [ ] Create `test_unregister.py` with unregister validation tests

### Phase 2 (Medium Priority)
- [ ] Add data integrity tests
- [ ] Add edge case tests
- [ ] Generate coverage reports

### Phase 3 (Nice to Have)
- [ ] Add performance tests
- [ ] Add concurrent request tests
- [ ] Integration tests with frontend

---

## Notes

- Tests use an in-memory database (no external dependencies)
- Each test should be independent and not rely on test order
- Use descriptive test names following `test_<function>_<scenario>` pattern
- Keep tests focused: one assertion per test when possible
