"""
Pytest configuration and shared fixtures for all tests.

This file implements the ARRANGE phase of the AAA (Arrange-Act-Assert) pattern
by providing reusable fixtures for test setup and preconditions.
"""

import pytest
from fastapi.testclient import TestClient
import src.app


@pytest.fixture(autouse=True)
def reset_activities():
    """
    ARRANGE: Reset activities database to initial state before each test.
    
    This fixture ensures test isolation by resetting the in-memory database
    before each test runs. The autouse=True means it runs automatically.
    
    Yields:
        None: Fixture just resets state, doesn't return anything
    """
    # Reset the activities dictionary before each test
    src.app.activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in games",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Track and Field": {
            "description": "Train for running, jumping, and throwing events",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Art Club": {
            "description": "Explore drawing, painting, and other visual arts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Develop acting skills and stage a school production",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Debate Club": {
            "description": "Build research, reasoning, and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Explore scientific ideas through experiments and projects",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": []
        }
    }
    yield
    # Teardown happens after yield (database is reset for next test)


@pytest.fixture
def client():
    """
    ARRANGE: Provides a TestClient for making requests to the FastAPI app.
    
    This fixture is used in the ARRANGE phase of tests to set up
    the client that will be used in the ACT phase.
    
    Yields:
        TestClient: A test client for making HTTP requests
    """
    test_client = TestClient(src.app.app)
    yield test_client


@pytest.fixture
def sample_activity():
    """
    ARRANGE: Provides a known activity name for testing.
    
    Returns a valid activity that exists in the app's activities database.
    
    Returns:
        str: Activity name "Chess Club"
    """
    return "Chess Club"


@pytest.fixture
def sample_email():
    """
    ARRANGE: Provides a test email that is NOT already registered.
    
    This email can be used in signup tests to ensure we're testing
    new participant registration (not duplicate prevention).
    
    Returns:
        str: A unique test email address
    """
    return "newtester@example.com"


@pytest.fixture
def existing_participant():
    """
    ARRANGE: Provides an email that's already registered in Chess Club.
    
    This email is used in tests for duplicate prevention and
    unregister operations.
    
    Returns:
        str: An email already registered in activities
    """
    return "michael@mergington.edu"


@pytest.fixture
def another_activity():
    """
    ARRANGE: Provides a different activity for testing.
    
    Used to verify that operations on one activity don't affect others.
    
    Returns:
        str: Activity name "Programming Class"
    """
    return "Programming Class"
